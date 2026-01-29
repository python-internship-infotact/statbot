"""
StatBot Pro - Autonomous Data Analysis Agent
Enhanced with comprehensive error handling, security, and production features.

This module provides:
- Secure code execution with comprehensive sandboxing
- Self-correcting agent behavior with intelligent retry logic
- Advanced data analysis capabilities
- Comprehensive error handling and logging
- Production-ready security measures
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for production
import io
import uuid
import os
import sys
import traceback
import re
import ast
import signal
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    # resource module not available on Windows
    HAS_RESOURCE = False
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import threading
import time
from datetime import datetime
import warnings

# Suppress matplotlib warnings in production
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

logger = logging.getLogger(__name__)

# Custom exceptions for better error handling
class AgentError(Exception):
    """Base exception for agent-related errors"""
    pass

class SecurityError(AgentError):
    """Raised when security violations are detected"""
    pass

class ExecutionError(AgentError):
    """Raised when code execution fails"""
    pass

class ValidationError(AgentError):
    """Raised when input validation fails"""
    pass

class TimeoutError(AgentError):
    """Raised when execution times out"""
    pass

class SecureExecutor:
    """
    Production-ready secure code executor with comprehensive sandboxing.
    
    Features:
    - Restricted module imports and built-in functions
    - Memory and CPU usage limits
    - Execution timeout with proper cleanup
    - AST-based code validation
    - Comprehensive logging and monitoring
    """
    
    # Allowed modules with their safe imports
    ALLOWED_MODULES = {
        'pandas': pd,
        'pd': pd,
        'numpy': np,
        'np': np,
        'matplotlib': matplotlib,
        'plt': plt,
        'math': __import__('math'),
        'datetime': __import__('datetime'),
        'statistics': __import__('statistics')
    }
    
    # Completely blocked built-in functions
    BLOCKED_BUILTINS = {
        'open', 'exec', 'eval', 'compile', '__import__', 'input', 
        'raw_input', 'file', 'execfile', 'reload', 'vars', 'dir',
        'globals', 'locals', 'delattr', 'setattr', 'getattr',
        'hasattr', 'callable', 'isinstance', 'issubclass',
        'super', 'property', 'staticmethod', 'classmethod'
    }
    
    # Dangerous AST node types that should be blocked
    BLOCKED_AST_NODES = {
        ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef,
        ast.ClassDef, ast.Global, ast.Nonlocal, ast.Delete,
        ast.With, ast.AsyncWith, ast.Try, ast.ExceptHandler,
        ast.Raise, ast.Assert
    }
    
    # Dangerous attribute access patterns
    BLOCKED_ATTRIBUTES = {
        '__class__', '__bases__', '__subclasses__', '__mro__',
        '__dict__', '__globals__', '__locals__', '__code__',
        '__func__', '__self__', '__module__', '__qualname__'
    }
    
    # Resource limits
    MAX_MEMORY_MB = 512  # Maximum memory usage in MB
    MAX_CPU_TIME = 30    # Maximum CPU time in seconds
    MAX_OUTPUT_SIZE = 10000  # Maximum output string length
    
    def __init__(self, timeout: int = 30):
        """
        Initialize secure executor with configuration.
        
        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
        self.static_dir = Path("static")
        self.static_dir.mkdir(exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="SecureExec")
        
        # Set up resource limits
        self._setup_resource_limits()
    
    def _setup_resource_limits(self):
        """Set up system resource limits"""
        if not HAS_RESOURCE:
            logger.warning("Resource module not available (Windows). Resource limits disabled.")
            return
            
        try:
            # Set memory limit (if supported on the platform)
            if hasattr(resource, 'RLIMIT_AS'):
                resource.setrlimit(
                    resource.RLIMIT_AS, 
                    (self.MAX_MEMORY_MB * 1024 * 1024, self.MAX_MEMORY_MB * 1024 * 1024)
                )
            
            # Set CPU time limit
            if hasattr(resource, 'RLIMIT_CPU'):
                resource.setrlimit(
                    resource.RLIMIT_CPU,
                    (self.MAX_CPU_TIME, self.MAX_CPU_TIME)
                )
                
        except (OSError, ValueError) as e:
            logger.warning(f"Could not set resource limits: {e}")
    
    def _validate_code_ast(self, code: str) -> None:
        """
        Validate code using AST analysis to detect dangerous constructs.
        
        Args:
            code: Python code to validate
            
        Raises:
            SecurityError: If dangerous constructs are found
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SecurityError(f"Syntax error in code: {e}")
        
        # Check for blocked AST nodes
        for node in ast.walk(tree):
            if type(node) in self.BLOCKED_AST_NODES:
                raise SecurityError(f"Blocked construct detected: {type(node).__name__}")
            
            # Check for dangerous attribute access
            if isinstance(node, ast.Attribute):
                if node.attr in self.BLOCKED_ATTRIBUTES:
                    raise SecurityError(f"Blocked attribute access: {node.attr}")
            
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.BLOCKED_BUILTINS:
                        raise SecurityError(f"Blocked function call: {node.func.id}")
    
    def _validate_code_patterns(self, code: str) -> None:
        """
        Validate code using pattern matching for additional security.
        
        Args:
            code: Python code to validate
            
        Raises:
            SecurityError: If dangerous patterns are found
        """
        dangerous_patterns = [
            r'__.*__',  # Dunder methods
            r'import\s+os',
            r'import\s+sys',
            r'import\s+subprocess',
            r'from\s+os',
            r'from\s+sys',
            r'from\s+subprocess',
            r'exec\s*\(',
            r'eval\s*\(',
            r'compile\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
            r'\.system\s*\(',
            r'\.popen\s*\(',
            r'\.call\s*\(',
            r'\.run\s*\(',
            r'\.Popen\s*\(',
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, code_lower):
                raise SecurityError(f"Dangerous pattern detected: {pattern}")
    
    def _create_safe_globals(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create a safe global namespace for code execution.
        
        Args:
            df: DataFrame to include in the namespace
            
        Returns:
            Safe global namespace dictionary
        """
        # Create restricted builtins
        safe_builtins = {}
        for name, obj in __builtins__.items():
            if name not in self.BLOCKED_BUILTINS:
                # Only allow safe built-ins
                if name in ['len', 'str', 'int', 'float', 'bool', 'list', 'dict', 
                           'tuple', 'set', 'range', 'enumerate', 'zip', 'sorted',
                           'sum', 'min', 'max', 'abs', 'round', 'type', 'print']:
                    safe_builtins[name] = obj
        
        safe_globals = {
            '__builtins__': safe_builtins,
            '__name__': '__main__',
            '__doc__': None,
        }
        
        # Add allowed modules
        safe_globals.update(self.ALLOWED_MODULES)
        
        # Add the dataframe
        safe_globals['df'] = df.copy()  # Use copy to prevent modification
        
        return safe_globals
    
    def _execute_with_monitoring(self, code: str, safe_globals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code with comprehensive monitoring and resource tracking.
        
        Args:
            code: Python code to execute
            safe_globals: Safe global namespace
            
        Returns:
            Execution result dictionary
        """
        start_time = time.time()
        safe_locals = {}
        
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        captured_output = io.StringIO()
        captured_errors = io.StringIO()
        
        try:
            sys.stdout = captured_output
            sys.stderr = captured_errors
            
            # Execute the code
            exec(code, safe_globals, safe_locals)
            
            # Get outputs
            output = captured_output.getvalue()
            errors = captured_errors.getvalue()
            
            # Limit output size
            if len(output) > self.MAX_OUTPUT_SIZE:
                output = output[:self.MAX_OUTPUT_SIZE] + "\n... (output truncated)"
            
            # Check if a plot was created
            chart_url = None
            if plt.get_fignums():
                chart_filename = f"chart_{uuid.uuid4().hex}.png"
                chart_path = self.static_dir / chart_filename
                
                try:
                    plt.savefig(chart_path, dpi=150, bbox_inches='tight', 
                               facecolor='white', edgecolor='none')
                    chart_url = f"/static/{chart_filename}"
                    logger.info(f"Chart saved: {chart_path}")
                except Exception as e:
                    logger.error(f"Error saving chart: {e}")
                finally:
                    plt.close('all')
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'output': output.strip(),
                'errors': errors.strip(),
                'chart_url': chart_url,
                'execution_time': execution_time,
                'locals': {k: str(v)[:200] for k, v in safe_locals.items() 
                          if not k.startswith('_')}
            }
            
        except MemoryError:
            raise ExecutionError("Code execution exceeded memory limits")
        except KeyboardInterrupt:
            raise ExecutionError("Code execution was interrupted")
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc(),
                'execution_time': execution_time
            }
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            plt.close('all')  # Ensure all plots are closed
    
    def execute_code(self, code: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute code in a secure sandboxed environment with comprehensive validation.
        
        Args:
            code: Python code to execute
            df: DataFrame for analysis
            
        Returns:
            Execution result dictionary
            
        Raises:
            SecurityError: If security validation fails
            ExecutionError: If execution fails
            TimeoutError: If execution times out
        """
        logger.info(f"Starting secure code execution (timeout: {self.timeout}s)")
        
        try:
            # Comprehensive code validation
            self._validate_code_ast(code)
            self._validate_code_patterns(code)
            
            # Create safe execution environment
            safe_globals = self._create_safe_globals(df)
            
            # Execute with timeout using thread pool
            future = self.executor.submit(self._execute_with_monitoring, code, safe_globals)
            
            try:
                result = future.result(timeout=self.timeout)
                
                if result['success']:
                    logger.info(f"Code execution successful (time: {result['execution_time']:.2f}s)")
                else:
                    logger.warning(f"Code execution failed: {result.get('error', 'Unknown error')}")
                
                return result
                
            except FutureTimeoutError:
                future.cancel()
                raise TimeoutError(f"Code execution timed out after {self.timeout} seconds")
                
        except (SecurityError, ExecutionError, TimeoutError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in code execution: {e}")
            raise ExecutionError(f"Unexpected execution error: {str(e)}")
    
    def __del__(self):
        """Cleanup executor on deletion"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

class StatBotAgent:
    """
    Production-ready autonomous data analysis agent with comprehensive capabilities.
    
    Features:
    - Intelligent question analysis and code generation
    - Self-correcting behavior with advanced retry logic
    - Comprehensive error handling and recovery
    - Security-first design with validation
    - Advanced data analysis capabilities
    - Detailed logging and monitoring
    """
    
    def __init__(self, max_retries: int = 3, timeout: int = 30):
        """
        Initialize the StatBot agent.
        
        Args:
            max_retries: Maximum number of retry attempts
            timeout: Execution timeout in seconds
        """
        self.executor = SecureExecutor(timeout=timeout)
        self.max_retries = max_retries
        self.question_patterns = self._initialize_question_patterns()
        self.code_templates = self._initialize_code_templates()
        
        logger.info(f"StatBot Agent initialized (retries: {max_retries}, timeout: {timeout}s)")
    
    def _initialize_question_patterns(self) -> Dict[str, List[str]]:
        """Initialize question pattern recognition"""
        return {
            'correlation': [
                'correlation', 'correlate', 'relationship', 'relate', 'association',
                'connected', 'linked', 'dependent', 'corr'
            ],
            'visualization': [
                'plot', 'chart', 'graph', 'visualize', 'show', 'display', 'draw',
                'histogram', 'scatter', 'line', 'bar', 'heatmap', 'distribution'
            ],
            'statistics': [
                'mean', 'average', 'median', 'mode', 'std', 'variance', 'summary',
                'statistics', 'describe', 'count', 'sum', 'min', 'max', 'quantile'
            ],
            'comparison': [
                'compare', 'difference', 'versus', 'vs', 'between', 'highest',
                'lowest', 'best', 'worst', 'top', 'bottom', 'rank'
            ],
            'trend': [
                'trend', 'over time', 'temporal', 'time series', 'change',
                'growth', 'decline', 'pattern', 'seasonal'
            ],
            'grouping': [
                'group', 'category', 'segment', 'by region', 'by type',
                'breakdown', 'split', 'partition'
            ],
            'outliers': [
                'outlier', 'anomaly', 'unusual', 'abnormal', 'extreme',
                'deviation', 'exception'
            ]
        }
    
    def _initialize_code_templates(self) -> Dict[str, str]:
        """Initialize code generation templates"""
        return {
            'basic_info': """
# Dataset Overview
print(f'Dataset shape: {df.shape}')
print(f'Columns: {list(df.columns)}')
print(f'Data types:\\n{df.dtypes}')
print(f'Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB')
""",
            'missing_data': """
# Missing Data Analysis
missing_data = df.isnull().sum()
missing_percent = (missing_data / len(df)) * 100
missing_info = pd.DataFrame({
    'Missing Count': missing_data,
    'Missing Percentage': missing_percent
})
print('Missing Data Summary:')
print(missing_info[missing_info['Missing Count'] > 0])
""",
            'summary_stats': """
# Summary Statistics
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    print('Summary Statistics for Numeric Columns:')
    print(df[numeric_cols].describe())
else:
    print('No numeric columns found for summary statistics')
""",
            'correlation_analysis': """
# Correlation Analysis
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 1:
    correlation_matrix = df[numeric_cols].corr()
    print('Correlation Matrix:')
    print(correlation_matrix)
    
    # Find strongest correlations
    corr_pairs = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            col1, col2 = correlation_matrix.columns[i], correlation_matrix.columns[j]
            corr_val = correlation_matrix.iloc[i, j]
            corr_pairs.append((col1, col2, abs(corr_val), corr_val))
    
    corr_pairs.sort(key=lambda x: x[2], reverse=True)
    print('\\nStrongest Correlations:')
    for col1, col2, abs_corr, corr in corr_pairs[:5]:
        print(f'{col1} - {col2}: {corr:.3f}')
else:
    print('Need at least 2 numeric columns for correlation analysis')
""",
            'distribution_plot': """
# Distribution Analysis
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    n_cols = min(3, len(numeric_cols))
    fig, axes = plt.subplots(1, n_cols, figsize=(5*n_cols, 4))
    if n_cols == 1:
        axes = [axes]
    
    for i, col in enumerate(numeric_cols[:n_cols]):
        axes[i].hist(df[col].dropna(), bins=20, alpha=0.7, edgecolor='black')
        axes[i].set_title(f'{col} Distribution')
        axes[i].set_xlabel(col)
        axes[i].set_ylabel('Frequency')
        axes[i].grid(True, alpha=0.3)
    
    plt.tight_layout()
    print(f'Distribution plots created for {n_cols} numeric columns')
else:
    print('No numeric columns found for distribution analysis')
""",
            'correlation_heatmap': """
# Correlation Heatmap
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 1:
    correlation_matrix = df[numeric_cols].corr()
    
    plt.figure(figsize=(10, 8))
    im = plt.imshow(correlation_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
    plt.colorbar(im, label='Correlation Coefficient')
    
    # Add labels
    plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=45, ha='right')
    plt.yticks(range(len(correlation_matrix.columns)), correlation_matrix.columns)
    
    # Add correlation values as text
    for i in range(len(correlation_matrix.columns)):
        for j in range(len(correlation_matrix.columns)):
            plt.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}', 
                    ha='center', va='center', fontsize=8)
    
    plt.title('Correlation Matrix Heatmap')
    plt.tight_layout()
    print('Correlation heatmap created')
else:
    print('Need at least 2 numeric columns for correlation heatmap')
""",
            'outlier_detection': """
# Outlier Detection using IQR method
numeric_cols = df.select_dtypes(include=[np.number]).columns
outlier_summary = {}

for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    outlier_summary[col] = {
        'count': len(outliers),
        'percentage': (len(outliers) / len(df)) * 100,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound
    }

print('Outlier Detection Summary:')
for col, info in outlier_summary.items():
    if info['count'] > 0:
        print(f'{col}: {info["count"]} outliers ({info["percentage"]:.1f}%)')
        print(f'  Valid range: {info["lower_bound"]:.2f} to {info["upper_bound"]:.2f}')
"""
        }
    
    def _analyze_question_intent(self, question: str) -> Dict[str, Any]:
        """
        Analyze question to determine intent and required analysis type.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with analysis intent and parameters
        """
        question_lower = question.lower()
        intent = {
            'primary_type': 'general',
            'requires_visualization': False,
            'analysis_types': [],
            'specific_columns': [],
            'complexity': 'simple'
        }
        
        # Check for different analysis types
        for analysis_type, keywords in self.question_patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                intent['analysis_types'].append(analysis_type)
        
        # Determine primary type
        if intent['analysis_types']:
            intent['primary_type'] = intent['analysis_types'][0]
        
        # Check if visualization is needed
        viz_keywords = self.question_patterns['visualization']
        intent['requires_visualization'] = any(keyword in question_lower for keyword in viz_keywords)
        
        # Extract specific column mentions (simple heuristic)
        words = question_lower.split()
        potential_columns = [word.strip('.,!?') for word in words if len(word) > 2]
        intent['potential_columns'] = potential_columns
        
        # Determine complexity
        if len(intent['analysis_types']) > 2 or 'comprehensive' in question_lower:
            intent['complexity'] = 'complex'
        elif len(intent['analysis_types']) > 1:
            intent['complexity'] = 'moderate'
        
        logger.info(f"Question intent analysis: {intent}")
        return intent
    
    def _generate_specific_query_code(self, question: str, schema_info: Dict[str, Any]) -> Optional[str]:
        """
        Generate code for specific filtering and aggregation queries.
        
        Args:
            question: Natural language question
            schema_info: DataFrame schema information
            
        Returns:
            Generated Python code or None if not a specific query
        """
        logger.info("=== ENTERING _generate_specific_query_code ===")
        question_lower = question.lower()
        available_cols = schema_info.get('columns', [])
        
        logger.info(f"Checking specific query patterns for: '{question_lower}'")
        
        # Pattern: "total [column] in [value]" or "sum of [column] in [value]"
        import re
        
        # Match patterns like "total marketing_spend in south"
        total_pattern = r'total\s+(\w+)\s+in\s+(\w+)'
        sum_pattern = r'sum\s+(?:of\s+)?(\w+)\s+in\s+(\w+)'
        
        match = re.search(total_pattern, question_lower) or re.search(sum_pattern, question_lower)
        
        if match:
            target_column = match.group(1)
            filter_value = match.group(2)
            
            logger.info(f"Specific query detected: column='{target_column}', filter='{filter_value}'")
            
            # Find the actual column name (case-insensitive match)
            actual_column = None
            for col in available_cols:
                if col.lower() == target_column:
                    actual_column = col
                    break
            
            if not actual_column:
                logger.warning(f"Column '{target_column}' not found in available columns: {available_cols}")
                return None
            
            # Find the filter column (likely categorical)
            categorical_cols = schema_info.get('categorical_columns', [])
            filter_column = None
            
            # Look for a column that might contain the filter value
            for col in categorical_cols:
                # This is a simple heuristic - in practice, you might want to check actual data
                if 'region' in col.lower() or 'category' in col.lower() or 'type' in col.lower():
                    filter_column = col
                    break
            
            if not filter_column and categorical_cols:
                filter_column = categorical_cols[0]  # Use first categorical column as fallback
            
            if filter_column:
                logger.info(f"Generating specific query code: {actual_column} in {filter_column} = {filter_value}")
                
                # Generate the correct filtering and aggregation code - simple string concatenation
                generated_code = f"""
# Specific Query: Total {actual_column} in {filter_value}
print('Available columns:', {available_cols})
print('Looking for {actual_column} in {filter_column} = {filter_value}')

# Check unique values in the filter column
print('\\nUnique values in {filter_column}:', df["{filter_column}"].unique())

# Find the correct case for the filter value
filter_values = df['{filter_column}'].unique()
target_value = None
for val in filter_values:
    if str(val).lower() == '{filter_value}':
        target_value = val
        break

if target_value is not None:
    # Filter and sum
    filtered_data = df[df['{filter_column}'] == target_value]
    total_value = filtered_data['{actual_column}'].sum()
    
    print('\\nTotal {actual_column} in', target_value, ':', total_value)
    
    # Show breakdown
    print('\\nBreakdown of {actual_column} in', target_value, ':')
    print(filtered_data[['{filter_column}', '{actual_column}']])
    
    # Show summary
    print('\\nSummary:')
    print('- Number of records:', len(filtered_data))
    print('- Total {actual_column}:', total_value)
    print('- Average {actual_column}:', total_value/len(filtered_data))
else:
    print('\\nValue "{filter_value}" not found in {filter_column}')
    print('Available values:', list(filter_values))
"""
                logger.info(f"Generated code preview: {generated_code[:200]}...")
                return generated_code
            else:
                logger.warning(f"No suitable filter column found in categorical columns: {categorical_cols}")
        
        # Pattern: "[column] by [grouping_column]" or "group [column] by [grouping_column]"
        group_pattern = r'(?:group\s+)?(\w+)\s+by\s+(\w+)'
        group_match = re.search(group_pattern, question_lower)
        
        if group_match:
            target_column = group_match.group(1)
            group_column = group_match.group(2)
            
            logger.info(f"Group query detected: column='{target_column}', group_by='{group_column}'")
            
            # Find actual column names
            actual_target = None
            actual_group = None
            
            for col in available_cols:
                if col.lower() == target_column:
                    actual_target = col
                if col.lower() == group_column:
                    actual_group = col
            
            if actual_target and actual_group:
                logger.info(f"Generating group query code: {actual_target} by {actual_group}")
                return f"""
# Group Analysis: {actual_target} by {actual_group}
print('Grouping {actual_target} by {actual_group}')

# Group and aggregate
grouped_data = df.groupby('{actual_group}')['{actual_target}'].agg(['sum', 'mean', 'count'])
print('\\nGrouped Results:')
print(grouped_data)

# Find highest and lowest
highest_sum = grouped_data['sum'].idxmax()
lowest_sum = grouped_data['sum'].idxmin()

print(f'\\nHighest total {actual_target}: {{highest_sum}} ({{grouped_data.loc[highest_sum, "sum"]:,.2f}})')
print(f'Lowest total {actual_target}: {{lowest_sum}} ({{grouped_data.loc[lowest_sum, "sum"]:,.2f}})')

# Create visualization
grouped_data['sum'].plot(kind='bar', title=f'{actual_target} by {actual_group}')
plt.ylabel(f'Total {actual_target}')
plt.xlabel(actual_group)
plt.xticks(rotation=45)
plt.tight_layout()
"""
            else:
                logger.warning(f"Columns not found: target='{target_column}' -> {actual_target}, group='{group_column}' -> {actual_group}")
        
        logger.info("No specific query pattern matched, using general analysis")
        return None
    
    def _generate_analysis_code(self, question: str, schema_info: Dict[str, Any], intent: Dict[str, Any]) -> str:
        """
        Generate Python code based on question analysis and data schema.
        
        Args:
            question: Original question
            schema_info: DataFrame schema information
            intent: Question intent analysis
            
        Returns:
            Generated Python code
        """
        logger.info(f"Generating analysis code for question: '{question}'")
        
        # Check for specific filtering and aggregation patterns first
        specific_code = self._generate_specific_query_code(question, schema_info)
        logger.info(f"Specific query code result: {specific_code is not None}")
        if specific_code:
            logger.info("Using specific query code")
            return specific_code
        
        logger.info("Using general analysis code")
        code_parts = [self.code_templates['basic_info']]
        
        # Add missing data analysis for complex questions
        if intent['complexity'] in ['moderate', 'complex']:
            code_parts.append(self.code_templates['missing_data'])
        
        # Generate code based on primary analysis type
        primary_type = intent['primary_type']
        
        if primary_type == 'correlation':
            code_parts.append(self.code_templates['correlation_analysis'])
            if intent['requires_visualization']:
                code_parts.append(self.code_templates['correlation_heatmap'])
        
        elif primary_type == 'statistics':
            code_parts.append(self.code_templates['summary_stats'])
            if intent['requires_visualization']:
                code_parts.append(self.code_templates['distribution_plot'])
        
        elif primary_type == 'visualization':
            if 'correlation' in intent['analysis_types']:
                code_parts.append(self.code_templates['correlation_heatmap'])
            else:
                code_parts.append(self.code_templates['distribution_plot'])
        
        elif primary_type == 'outliers':
            code_parts.append(self.code_templates['outlier_detection'])
        
        elif primary_type == 'comparison':
            # Generate comparison code
            numeric_cols = schema_info.get('numeric_columns', [])
            categorical_cols = schema_info.get('categorical_columns', [])
            
            if numeric_cols and categorical_cols:
                comparison_code = f"""
# Comparison Analysis
categorical_col = '{categorical_cols[0]}'
numeric_col = '{numeric_cols[0]}'

print(f'Comparison of {{numeric_col}} by {{categorical_col}}:')
comparison_stats = df.groupby(categorical_col)[numeric_col].agg(['mean', 'median', 'std', 'count'])
print(comparison_stats)

# Find highest and lowest
highest = comparison_stats['mean'].idxmax()
lowest = comparison_stats['mean'].idxmin()
print(f'\\nHighest average {{numeric_col}}: {{highest}} ({{comparison_stats.loc[highest, "mean"]:.2f}})')
print(f'Lowest average {{numeric_col}}: {{lowest}} ({{comparison_stats.loc[lowest, "mean"]:.2f}})')
"""
                code_parts.append(comparison_code)
        
        else:
            # Default comprehensive analysis
            code_parts.append(self.code_templates['summary_stats'])
            if len(schema_info.get('numeric_columns', [])) > 1:
                code_parts.append(self.code_templates['correlation_analysis'])
        
        # Add visualization if requested and not already included
        if intent['requires_visualization'] and primary_type not in ['visualization', 'correlation']:
            code_parts.append(self.code_templates['distribution_plot'])
        
        return '\n'.join(code_parts)
    
    def _fix_code_intelligently(self, original_code: str, error: str, error_type: str, 
                               question: str, schema_info: Dict[str, Any], attempt: int) -> str:
        """
        Intelligently fix code based on error analysis.
        
        Args:
            original_code: Original failing code
            error: Error message
            error_type: Type of error
            question: Original question
            schema_info: DataFrame schema information
            attempt: Current attempt number
            
        Returns:
            Fixed code
        """
        logger.info(f"Attempting intelligent code fix (attempt {attempt}): {error_type}")
        
        available_cols = schema_info['columns']
        numeric_cols = schema_info['numeric_columns']
        categorical_cols = schema_info['categorical_columns']
        
        if error_type == 'KeyError' or 'KeyError' in error:
            # Column name issues - use available columns
            fixed_code = f"""
# Fixed analysis using available columns
print('Available columns:', {available_cols})
print('Numeric columns:', {numeric_cols})
print('Categorical columns:', {categorical_cols})

# Dataset overview
print(f'\\nDataset shape: {{df.shape}}')
print('\\nFirst few rows:')
print(df.head())

# Analysis based on available data
if len({numeric_cols}) > 0:
    print('\\nSummary statistics for numeric columns:')
    print(df{numeric_cols}.describe())
    
    if len({numeric_cols}) > 1:
        print('\\nCorrelation analysis:')
        corr_matrix = df{numeric_cols}.corr()
        print(corr_matrix)
        
        # Simple visualization
        plt.figure(figsize=(8, 6))
        plt.imshow(corr_matrix, cmap='coolwarm', aspect='auto')
        plt.colorbar(label='Correlation')
        plt.title('Correlation Matrix')
        plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=45)
        plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
        plt.tight_layout()

if len({categorical_cols}) > 0:
    print('\\nCategorical column analysis:')
    for col in {categorical_cols}[:2]:  # Analyze first 2 categorical columns
        print(f'\\n{{col}} value counts:')
        print(df[col].value_counts().head())
"""
            return fixed_code
        
        elif 'matplotlib' in error.lower() or 'plot' in error.lower():
            # Plotting issues - create simpler visualization
            return f"""
# Simplified analysis with basic plotting
print('Dataset Analysis:')
print(f'Shape: {{df.shape}}')
print(f'Columns: {{list(df.columns)}}')

# Basic statistics
if len({numeric_cols}) > 0:
    print('\\nNumeric column statistics:')
    print(df{numeric_cols}.describe())
    
    # Simple histogram for first numeric column
    col = {numeric_cols}[0]
    plt.figure(figsize=(8, 6))
    plt.hist(df[col].dropna(), bins=20, alpha=0.7, edgecolor='black')
    plt.title(f'{{col}} Distribution')
    plt.xlabel(col)
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    print(f'\\nHistogram created for {{col}}')
"""
        
        elif 'memory' in error.lower() or 'timeout' in error.lower():
            # Memory or timeout issues - create minimal analysis
            return f"""
# Minimal analysis for large dataset
print('Dataset Overview (Sample):')
print(f'Shape: {{df.shape}}')
print(f'Columns: {{list(df.columns)}}')

# Sample analysis to avoid memory issues
sample_size = min(1000, len(df))
df_sample = df.sample(n=sample_size, random_state=42)
print(f'\\nAnalyzing sample of {{sample_size}} rows:')

if len({numeric_cols}) > 0:
    print('\\nSample statistics:')
    print(df_sample{numeric_cols}.describe())
"""
        
        else:
            # Generic fallback with error-resistant code
            return f"""
# Error-resistant fallback analysis
try:
    print('Dataset Information:')
    print(f'Shape: {{df.shape}}')
    print(f'Columns: {{list(df.columns)}}')
    
    # Safe data type analysis
    print('\\nData Types:')
    for col in df.columns:
        print(f'{{col}}: {{df[col].dtype}}')
    
    # Safe sample display
    print('\\nSample Data:')
    print(df.head(3))
    
    # Safe numeric analysis
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_columns:
        print(f'\\nNumeric columns found: {{numeric_columns}}')
        for col in numeric_columns[:3]:  # Limit to first 3
            try:
                print(f'\\n{{col}} statistics:')
                print(f'  Mean: {{df[col].mean():.2f}}')
                print(f'  Median: {{df[col].median():.2f}}')
                print(f'  Std: {{df[col].std():.2f}}')
            except Exception as e:
                print(f'  Error analyzing {{col}}: {{str(e)}}')
    
except Exception as e:
    print(f'Analysis error: {{str(e)}}')
    print('Basic info only:')
    print(f'DataFrame shape: {{df.shape}}')
"""
    
    async def process_question(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """
        Process a natural language question with comprehensive error handling and retry logic.
        
        Args:
            df: DataFrame to analyze
            question: Natural language question
            
        Returns:
            Analysis results dictionary
            
        Raises:
            ValidationError: If input validation fails
            AgentError: If processing fails after all retries
        """
        start_time = time.time()
        
        # Input validation
        if df is None or df.empty:
            raise ValidationError("DataFrame is None or empty")
        
        if not question or not question.strip():
            raise ValidationError("Question is empty or None")
        
        logger.info(f"Processing question: '{question[:100]}...' for DataFrame shape {df.shape}")
        
        try:
            # Step 1: Analyze DataFrame schema
            schema_info = self._get_dataframe_info(df)
            logger.info("DataFrame schema analyzed")
            
            # Step 2: Analyze question intent
            intent = self._analyze_question_intent(question)
            logger.info(f"Question intent determined: {intent['primary_type']}")
            
            # Step 3: Generate and execute code with retries
            last_error = None
            last_error_type = None
            
            for attempt in range(1, self.max_retries + 1):
                try:
                    if attempt == 1:
                        # First attempt: generate code based on intent
                        code = self._generate_analysis_code(question, schema_info, intent)
                        logger.info("Initial analysis code generated")
                    else:
                        # Retry attempts: fix code based on previous error
                        code = self._fix_code_intelligently(
                            code, last_error, last_error_type, question, schema_info, attempt
                        )
                        logger.info(f"Code fixed for attempt {attempt}")
                    
                    # Execute code
                    result = self.executor.execute_code(code, df)
                    
                    if result['success']:
                        processing_time = time.time() - start_time
                        
                        # Determine analysis type
                        analysis_type = "computation"
                        if result.get('chart_url'):
                            analysis_type = "visualization"
                        elif intent['requires_visualization']:
                            analysis_type = "visualization_attempted"
                        
                        logger.info(f"Question processed successfully in {processing_time:.2f}s (attempt {attempt})")
                        
                        return {
                            'answer': result.get('output') or "Analysis completed successfully",
                            'chart_url': result.get('chart_url'),
                            'code_used': code,
                            'analysis_type': analysis_type,
                            'execution_time': result.get('execution_time', 0),
                            'processing_time': processing_time,
                            'attempts': attempt,
                            'dataframe_info': schema_info
                        }
                    else:
                        last_error = result.get('error', 'Unknown error')
                        last_error_type = result.get('error_type', 'Unknown')
                        
                        logger.warning(f"Execution failed (attempt {attempt}): {last_error}")
                        
                        if attempt == self.max_retries:
                            # Final attempt failed
                            processing_time = time.time() - start_time
                            return {
                                'answer': f"Analysis failed after {self.max_retries} attempts. Last error: {last_error}",
                                'error': last_error,
                                'error_type': last_error_type,
                                'code_used': code,
                                'analysis_type': "error",
                                'processing_time': processing_time,
                                'attempts': attempt
                            }
                
                except (SecurityError, TimeoutError) as e:
                    # Don't retry security violations or timeouts
                    logger.error(f"Non-retryable error: {e}")
                    raise
                
                except Exception as e:
                    last_error = str(e)
                    last_error_type = type(e).__name__
                    logger.error(f"Unexpected error (attempt {attempt}): {e}")
                    
                    if attempt == self.max_retries:
                        raise ExecutionError(f"Processing failed after {self.max_retries} attempts: {last_error}")
        
        except (ValidationError, SecurityError, TimeoutError):
            raise
        except Exception as e:
            logger.error(f"Critical error in question processing: {e}")
            raise AgentError(f"Critical processing error: {str(e)}")
    
    def _get_dataframe_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive information about the dataframe with error handling.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with dataframe information
        """
        try:
            # Basic info
            info = {
                'shape': df.shape,
                'columns': list(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum()
            }
            
            # Data types (safe conversion)
            try:
                info['dtypes'] = {col: str(dtype) for col, dtype in df.dtypes.items()}
            except Exception:
                info['dtypes'] = {}
            
            # Null counts (safe conversion)
            try:
                info['null_counts'] = {col: int(count) for col, count in df.isnull().sum().items()}
            except Exception:
                info['null_counts'] = {}
            
            # Sample data (safe conversion)
            try:
                info['sample_data'] = df.head(3).fillna("").to_dict('records')
            except Exception:
                info['sample_data'] = []
            
            # Column categorization
            try:
                info['numeric_columns'] = list(df.select_dtypes(include=[np.number]).columns)
                info['categorical_columns'] = list(df.select_dtypes(include=['object', 'category']).columns)
                info['datetime_columns'] = list(df.select_dtypes(include=['datetime64']).columns)
            except Exception:
                info['numeric_columns'] = []
                info['categorical_columns'] = []
                info['datetime_columns'] = []
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting dataframe info: {e}")
            # Return minimal safe info
            return {
                'shape': getattr(df, 'shape', (0, 0)),
                'columns': list(getattr(df, 'columns', [])),
                'dtypes': {},
                'null_counts': {},
                'sample_data': [],
                'numeric_columns': [],
                'categorical_columns': [],
                'datetime_columns': []
            }