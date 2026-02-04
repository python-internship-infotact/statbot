# Deployment Guide

This guide covers deploying StatBot Pro to Render (backend) and Vercel (frontend).

## Backend Deployment (Render)

### Prerequisites
- GitHub repository with your code
- Render account

### Steps

1. **Connect Repository to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: `statbot-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: Choose based on your needs (Free tier available)

3. **Environment Variables**
   Set these in Render dashboard:
   ```
   ENVIRONMENT=production
   PORT=8001
   HOST=0.0.0.0
   CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://statbot-frontend.vercel.app
   MAX_FILE_SIZE=52428800
   RATE_LIMIT_REQUESTS=100
   EXECUTION_TIMEOUT=30
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your service
   - Note the service URL (e.g., `https://statbot-backend.onrender.com`)

### Important Notes
- Free tier services sleep after 15 minutes of inactivity
- First request after sleep may take 30+ seconds
- Consider upgrading to paid tier for production use

## Frontend Deployment (Vercel)

### Prerequisites
- GitHub repository with your code
- Vercel account

### Steps

1. **Connect Repository to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

3. **Environment Variables**
   Set in Vercel dashboard:
   ```
   VITE_API_URL=https://your-render-backend-url.onrender.com
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your frontend
   - Note the deployment URL

### Custom Domain (Optional)
1. Go to Project Settings → Domains
2. Add your custom domain
3. Update CORS_ORIGINS in Render to include your custom domain

## Post-Deployment Configuration

### Update CORS Origins
After both services are deployed, update the backend's CORS configuration:

1. In Render dashboard, go to your backend service
2. Update the `CORS_ORIGINS` environment variable to include your Vercel URL:
   ```
   CORS_ORIGINS=https://your-project.vercel.app,http://localhost:3000
   ```
3. Redeploy the service

### Test Deployment
1. Visit your Vercel frontend URL
2. Try uploading a CSV file
3. Ask a question to test the full pipeline
4. Check both Render and Vercel logs for any issues

## Monitoring and Maintenance

### Render Monitoring
- Check service logs in Render dashboard
- Monitor service health and uptime
- Set up alerts for service failures

### Vercel Monitoring
- Check function logs in Vercel dashboard
- Monitor build and deployment status
- Review performance analytics

### Common Issues

1. **CORS Errors**
   - Ensure CORS_ORIGINS includes your frontend domain
   - Check that URLs don't have trailing slashes

2. **Service Sleeping (Render Free Tier)**
   - First request after sleep takes longer
   - Consider upgrading to paid tier
   - Implement health check pings if needed

3. **Build Failures**
   - Check build logs in respective dashboards
   - Ensure all dependencies are in package.json/requirements.txt
   - Verify environment variables are set correctly

4. **File Upload Issues**
   - Check file size limits
   - Ensure proper MIME type handling
   - Verify storage permissions

## Environment Variables Reference

### Backend (Render)
```
ENVIRONMENT=production
PORT=8001
HOST=0.0.0.0
CORS_ORIGINS=https://your-frontend.vercel.app
MAX_FILE_SIZE=52428800
RATE_LIMIT_REQUESTS=100
EXECUTION_TIMEOUT=30
MAX_RETRIES=3
LOG_LEVEL=info
```

### Frontend (Vercel)
```
VITE_API_URL=https://your-backend.onrender.com
```

## Security Considerations

1. **API Keys**: Never commit API keys to repository
2. **CORS**: Keep CORS origins restrictive
3. **Rate Limiting**: Configure appropriate rate limits
4. **File Validation**: Ensure proper file type validation
5. **Input Sanitization**: Validate all user inputs

## Scaling Considerations

1. **Backend**: Consider upgrading Render instance for better performance
2. **Frontend**: Vercel automatically scales
3. **Database**: Consider adding a database for session persistence
4. **CDN**: Use Vercel's built-in CDN for static assets
5. **Monitoring**: Implement proper logging and monitoring

## Support

For deployment issues:
1. Check service logs first
2. Verify environment variables
3. Test locally with production environment variables
4. Check platform-specific documentation (Render/Vercel)