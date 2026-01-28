# StatBot Pro - Production Deployment Guide

This guide covers production deployment, monitoring, and maintenance of StatBot Pro.

## 🏗️ Production Architecture

StatBot Pro is designed for production use with:

- **Secure Sandboxed Execution**: Code runs in isolated environment with restricted imports
- **Comprehensive Monitoring**: Real-time metrics, health checks, and alerting
- **Session Management**: Multi-user support with session isolation
- **Rate Limiting**: Protection against abuse and resource exhaustion
- **Error Recovery**: Self-correcting agent with intelligent retry logic
- **Resource Management**: Memory and CPU limits with automatic cleanup

## 🚀 Quick Production Deployment

### Option 1: Automated Deployment Script

```bash
# Local deployment
python deploy.py local

# Docker deployment (recommended)
python deploy.py docker
```

### Option 2: Manual Deployment

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export ENVIRONMENT=production
export PORT=8001
export WORKERS=4
export LOG_LEVEL=info

# 3. Start server
python main.py
```

### Option 3: Docker Deployment

```bash
# Build and run
docker-compose up --build -d

# Check status
docker-compose ps
docker-compose logs -f
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `production` | Deployment environment |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8001` | Server port |
| `WORKERS` | `4` | Number of worker processes |
| `LOG_LEVEL` | `info` | Logging level |
| `MAX_FILE_SIZE` | `52428800` | Max upload size (50MB) |
| `MAX_ROWS` | `100000` | Max CSV rows |
| `MAX_COLUMNS` | `1000` | Max CSV columns |
| `RATE_LIMIT_REQUESTS` | `100` | Requests per hour per IP |
| `EXECUTION_TIMEOUT` | `30` | Code execution timeout (seconds) |
| `MAX_RETRIES` | `3` | Agent retry attempts |
| `CLEANUP_INTERVAL` | `3600` | File cleanup interval (seconds) |

### Configuration Files

- `config.py` - Main configuration management
- `deployment_config.json` - Deployment-specific settings
- `docker-compose.yml` - Docker configuration

## 📊 Monitoring & Observability

### Health Checks

```bash
# Basic health check
curl http://localhost:8001/health

# Detailed health with system metrics
curl http://localhost:8001/health | jq
```

### Metrics Endpoints

```bash
# Application metrics (JSON)
curl http://localhost:8001/metrics

# Prometheus metrics
curl http://localhost:8001/metrics/prometheus
```

### Key Metrics

- **Request Metrics**: Total requests, success rate, response times
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Active sessions, charts generated, errors
- **Security Metrics**: Rate limit violations, security errors

### Log Files

- `logs/statbot.log` - Application logs
- `logs/deployment.log` - Deployment logs
- `logs/deployment_report.json` - Deployment report

## 🔒 Security Features

### Sandboxed Execution

- **Restricted Imports**: Only pandas, numpy, matplotlib, math allowed
- **Blocked Built-ins**: No file system, network, or system access
- **AST Validation**: Code analyzed before execution
- **Resource Limits**: Memory and CPU constraints
- **Execution Timeout**: Prevents infinite loops

### Input Validation

- **File Type Validation**: Only CSV files accepted
- **Size Limits**: Configurable file and data size limits
- **Content Sanitization**: Dangerous patterns blocked
- **Rate Limiting**: Per-IP request limits

### Session Security

- **Session Isolation**: Each upload gets unique session
- **Automatic Cleanup**: Old sessions and files removed
- **No Cross-Session Access**: Sessions cannot access each other's data

## 🔧 Maintenance

### Regular Tasks

1. **Log Rotation**: Set up logrotate for log files
2. **Disk Cleanup**: Monitor disk usage, old files cleaned automatically
3. **Security Updates**: Keep dependencies updated
4. **Monitoring**: Check metrics and alerts regularly

### Backup Strategy

```bash
# Backup configuration
tar -czf backup-config-$(date +%Y%m%d).tar.gz config.py docker-compose.yml

# Backup logs (if needed)
tar -czf backup-logs-$(date +%Y%m%d).tar.gz logs/
```

### Updates

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
docker-compose restart  # For Docker
# or
systemctl restart statbot  # For systemd service
```

## 📈 Performance Tuning

### Resource Optimization

```bash
# Environment variables for performance
export WORKERS=4                    # CPU cores
export MAX_MEMORY_MB=512           # Memory limit per process
export EXECUTION_TIMEOUT=30        # Balance speed vs complexity
export CLEANUP_INTERVAL=1800       # More frequent cleanup
```

### Database Integration (Future)

For high-volume deployments, consider:
- PostgreSQL for session storage
- Redis for caching
- Separate worker processes

## 🚨 Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Check memory usage
curl http://localhost:8001/health | jq '.system.memory_usage_percent'

# Reduce limits
export MAX_ROWS=50000
export MAX_FILE_SIZE=25000000
```

#### Slow Response Times
```bash
# Check response times
curl http://localhost:8001/metrics | jq '.request_metrics.avg_response_time'

# Optimize
export EXECUTION_TIMEOUT=15
export WORKERS=6
```

#### Rate Limiting Issues
```bash
# Check rate limit status
curl http://localhost:8001/metrics | jq '.counters'

# Adjust limits
export RATE_LIMIT_REQUESTS=200
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug
export ENVIRONMENT=development

# Restart service
python main.py
```

### Health Check Failures

```bash
# Check system resources
curl http://localhost:8001/health

# Check logs
tail -f logs/statbot.log

# Check Docker status
docker-compose ps
docker-compose logs statbot-pro
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy StatBot Pro

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: python -m pytest test_examples.py -v
      
      - name: Deploy
        run: python deploy.py docker
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: statbot-pro
spec:
  replicas: 3
  selector:
    matchLabels:
      app: statbot-pro
  template:
    metadata:
      labels:
        app: statbot-pro
    spec:
      containers:
      - name: statbot-pro
        image: statbot-pro:latest
        ports:
        - containerPort: 8001
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: WORKERS
          value: "1"
        resources:
          limits:
            memory: "1Gi"
            cpu: "500m"
          requests:
            memory: "512Mi"
            cpu: "250m"
```

## 📞 Support & Monitoring

### Alerting Setup

Configure alerts for:
- High error rates (>5%)
- High response times (>10s)
- High resource usage (>90%)
- Service downtime

### Monitoring Integration

- **Prometheus**: Use `/metrics/prometheus` endpoint
- **Grafana**: Create dashboards for key metrics
- **ELK Stack**: Centralized log analysis
- **Datadog/New Relic**: APM integration

### Production Checklist

- [ ] Environment variables configured
- [ ] SSL/TLS certificates installed
- [ ] Reverse proxy configured (nginx/Apache)
- [ ] Firewall rules applied
- [ ] Monitoring and alerting set up
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Security audit performed

## 🎯 Best Practices

1. **Security First**: Always run behind reverse proxy with SSL
2. **Monitor Everything**: Set up comprehensive monitoring
3. **Resource Limits**: Configure appropriate limits for your environment
4. **Regular Updates**: Keep dependencies and system updated
5. **Backup Strategy**: Regular backups of configuration and logs
6. **Testing**: Automated testing in CI/CD pipeline
7. **Documentation**: Keep deployment documentation updated

## 📚 Additional Resources

- [FastAPI Production Guide](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)
- [Prometheus Monitoring](https://prometheus.io/docs/guides/getting-started/)
- [Security Hardening Guide](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)

---

For issues or questions, check the logs first, then review this guide. The system is designed to be self-healing and provide detailed error information.