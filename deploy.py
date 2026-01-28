#!/usr/bin/env python3
"""
Production deployment script for StatBot Pro
Handles comprehensive deployment with monitoring, testing, and configuration
"""

import subprocess
import sys
import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeploymentManager:
    """Manages StatBot Pro deployment process"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "deployment_config.json"
        self.log_file = self.base_dir / "logs" / "deployment.log"
        
        # Ensure logs directory exists
        self.log_file.parent.mkdir(exist_ok=True)
    
    def check_requirements(self) -> bool:
        """Check if all required tools are installed"""
        logger.info("Checking deployment requirements...")
        
        requirements = [
            ("python", "Python 3.8+", ["python", "--version"]),
            ("pip", "Python package manager", ["pip", "--version"]),
            ("docker", "Docker (optional)", ["docker", "--version"]),
            ("docker-compose", "Docker Compose (optional)", ["docker-compose", "--version"])
        ]
        
        all_good = True
        for cmd, name, check_cmd in requirements:
            try:
                result = subprocess.run(check_cmd, capture_output=True, check=True, text=True)
                logger.info(f"✅ {name}: {result.stdout.strip().split()[0]} {result.stdout.strip().split()[1] if len(result.stdout.strip().split()) > 1 else ''}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                if cmd in ["docker", "docker-compose"]:
                    logger.warning(f"⚠️  {name} not found (optional for local deployment)")
                else:
                    logger.error(f"❌ {name} not found or not in PATH")
                    all_good = False
        
        return all_good
    
    def create_deployment_config(self) -> Dict[str, Any]:
        """Create deployment configuration"""
        config = {
            "deployment": {
                "timestamp": time.time(),
                "environment": os.getenv("ENVIRONMENT", "production"),
                "version": "1.0.0"
            },
            "server": {
                "host": os.getenv("HOST", "0.0.0.0"),
                "port": int(os.getenv("PORT", 8001)),
                "workers": int(os.getenv("WORKERS", 4)),
                "log_level": os.getenv("LOG_LEVEL", "info")
            },
            "security": {
                "max_file_size_mb": int(os.getenv("MAX_FILE_SIZE", 50)),
                "rate_limit_requests": int(os.getenv("RATE_LIMIT_REQUESTS", 100)),
                "execution_timeout": int(os.getenv("EXECUTION_TIMEOUT", 30))
            },
            "monitoring": {
                "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower() == "true",
                "cleanup_interval": int(os.getenv("CLEANUP_INTERVAL", 3600))
            }
        }
        
        # Save configuration
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Deployment configuration saved to {self.config_file}")
        return config
    
    def setup_environment(self) -> bool:
        """Set up the deployment environment"""
        logger.info("Setting up deployment environment...")
        
        try:
            # Create necessary directories
            directories = ["workspace", "static", "logs", "templates"]
            for dir_name in directories:
                dir_path = self.base_dir / dir_name
                dir_path.mkdir(exist_ok=True, mode=0o755)
                logger.info(f"✅ Directory created/verified: {dir_path}")
            
            # Install Python dependencies
            logger.info("Installing Python dependencies...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                capture_output=True, text=True, check=True
            )
            logger.info("✅ Python dependencies installed")
            
            # Run basic tests
            logger.info("Running basic validation tests...")
            self.run_validation_tests()
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Environment setup failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during setup: {e}")
            return False
    
    def run_validation_tests(self) -> bool:
        """Run validation tests before deployment"""
        logger.info("Running validation tests...")
        
        try:
            # Test imports
            test_imports = [
                "import pandas as pd",
                "import numpy as np",
                "import matplotlib.pyplot as plt",
                "import fastapi",
                "from agent import StatBotAgent",
                "from config import get_config",
                "from monitoring import metrics_collector"
            ]
            
            for import_test in test_imports:
                try:
                    exec(import_test)
                    logger.info(f"✅ Import test passed: {import_test}")
                except Exception as e:
                    logger.error(f"❌ Import test failed: {import_test} - {e}")
                    return False
            
            # Test configuration
            try:
                from config import get_config
                config = get_config()
                logger.info(f"✅ Configuration loaded: {config.ENVIRONMENT} environment")
            except Exception as e:
                logger.error(f"❌ Configuration test failed: {e}")
                return False
            
            # Test agent initialization
            try:
                from agent import StatBotAgent
                agent = StatBotAgent()
                logger.info("✅ Agent initialization test passed")
            except Exception as e:
                logger.error(f"❌ Agent initialization test failed: {e}")
                return False
            
            logger.info("✅ All validation tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Validation tests failed: {e}")
            return False
    
    def deploy_local(self) -> bool:
        """Deploy locally with Python"""
        logger.info("Starting local deployment...")
        
        try:
            # Start the server in background for testing
            logger.info("Starting server for deployment verification...")
            
            # Use subprocess to start server
            server_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            time.sleep(10)
            
            # Test server health
            if self.verify_deployment():
                logger.info("✅ Local deployment successful")
                
                # Stop test server
                server_process.terminate()
                server_process.wait(timeout=5)
                
                return True
            else:
                logger.error("❌ Deployment verification failed")
                server_process.terminate()
                return False
                
        except Exception as e:
            logger.error(f"❌ Local deployment failed: {e}")
            return False
    
    def deploy_docker(self) -> bool:
        """Deploy using Docker Compose"""
        logger.info("Starting Docker deployment...")
        
        try:
            # Build and start containers
            commands = [
                (["docker-compose", "down"], "Stopping existing containers"),
                (["docker-compose", "build", "--no-cache"], "Building Docker image"),
                (["docker-compose", "up", "-d"], "Starting containers")
            ]
            
            for cmd, description in commands:
                logger.info(f"Executing: {description}")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                logger.info(f"✅ {description} completed")
            
            # Wait for containers to be ready
            time.sleep(15)
            
            # Verify deployment
            if self.verify_deployment(port=8000):  # Docker uses port 8000
                logger.info("✅ Docker deployment successful")
                return True
            else:
                logger.error("❌ Docker deployment verification failed")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Docker deployment failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error in Docker deployment: {e}")
            return False
    
    def verify_deployment(self, port: int = 8001, max_retries: int = 5) -> bool:
        """Verify deployment by testing endpoints"""
        logger.info(f"Verifying deployment on port {port}...")
        
        base_url = f"http://localhost:{port}"
        
        # Test endpoints
        endpoints = [
            ("/health", "Health check"),
            ("/", "Web interface"),
            ("/metrics", "Metrics endpoint")
        ]
        
        for attempt in range(max_retries):
            try:
                all_passed = True
                
                for endpoint, description in endpoints:
                    try:
                        response = requests.get(f"{base_url}{endpoint}", timeout=10)
                        if response.status_code in [200, 503]:  # 503 is acceptable for health during startup
                            logger.info(f"✅ {description}: {response.status_code}")
                        else:
                            logger.warning(f"⚠️  {description}: {response.status_code}")
                            all_passed = False
                    except requests.exceptions.RequestException as e:
                        logger.warning(f"⚠️  {description}: Connection failed - {e}")
                        all_passed = False
                
                if all_passed:
                    logger.info("✅ Deployment verification successful")
                    return True
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying verification (attempt {attempt + 2}/{max_retries})...")
                    time.sleep(5)
                
            except Exception as e:
                logger.error(f"Verification attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
        
        logger.error("❌ Deployment verification failed after all retries")
        return False
    
    def generate_deployment_report(self, success: bool, deployment_type: str) -> None:
        """Generate deployment report"""
        report = {
            "deployment": {
                "timestamp": time.time(),
                "success": success,
                "type": deployment_type,
                "environment": os.getenv("ENVIRONMENT", "production")
            },
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(self.base_dir)
            }
        }
        
        if success:
            report["endpoints"] = {
                "web_interface": f"http://localhost:{os.getenv('PORT', 8001)}",
                "health_check": f"http://localhost:{os.getenv('PORT', 8001)}/health",
                "metrics": f"http://localhost:{os.getenv('PORT', 8001)}/metrics"
            }
            
            report["next_steps"] = [
                "Access the web interface to upload CSV files",
                "Monitor application health via /health endpoint",
                "Check metrics at /metrics endpoint",
                "Review logs in the logs/ directory"
            ]
        
        # Save report
        report_file = self.base_dir / "logs" / "deployment_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Deployment report saved to {report_file}")
        
        # Print summary
        if success:
            print("\n" + "="*60)
            print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"🌐 Web Interface: {report['endpoints']['web_interface']}")
            print(f"💚 Health Check: {report['endpoints']['health_check']}")
            print(f"📊 Metrics: {report['endpoints']['metrics']}")
            print("\n📋 Next Steps:")
            for step in report["next_steps"]:
                print(f"   • {step}")
            print("\n🚀 StatBot Pro is ready for production use!")
        else:
            print("\n" + "="*60)
            print("❌ DEPLOYMENT FAILED")
            print("="*60)
            print("Please check the logs for detailed error information.")
            print(f"Log file: {self.log_file}")

def main():
    """Main deployment function"""
    print("🤖 StatBot Pro Production Deployment")
    print("="*50)
    
    # Parse command line arguments
    deployment_type = "local"
    if len(sys.argv) > 1:
        deployment_type = sys.argv[1].lower()
    
    if deployment_type not in ["local", "docker"]:
        print("Usage: python deploy.py [local|docker]")
        sys.exit(1)
    
    print(f"🎯 Deployment type: {deployment_type}")
    
    # Initialize deployment manager
    deployer = DeploymentManager()
    
    try:
        # Check requirements
        if not deployer.check_requirements():
            print("\n❌ Requirements check failed. Please install missing dependencies.")
            sys.exit(1)
        
        # Create deployment configuration
        config = deployer.create_deployment_config()
        print(f"📋 Configuration created for {config['deployment']['environment']} environment")
        
        # Setup environment
        if not deployer.setup_environment():
            print("\n❌ Environment setup failed")
            sys.exit(1)
        
        # Deploy based on type
        success = False
        if deployment_type == "docker":
            success = deployer.deploy_docker()
        else:
            success = deployer.deploy_local()
        
        # Generate report
        deployer.generate_deployment_report(success, deployment_type)
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during deployment: {e}")
        print(f"\n❌ Deployment failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()