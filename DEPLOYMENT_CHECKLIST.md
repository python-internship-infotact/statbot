# Deployment Checklist

## Pre-Deployment

- [ ] Code is committed and pushed to GitHub
- [ ] All tests pass locally
- [ ] Environment variables are documented
- [ ] Dependencies are up to date in requirements.txt and package.json
- [ ] Build scripts work locally

## Backend Deployment (Render)

- [ ] Repository connected to Render
- [ ] Service configured with correct settings:
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `python start.py`
  - [ ] Environment: Python 3
- [ ] Environment variables set:
  - [ ] `ENVIRONMENT=production`
  - [ ] `PORT=8001`
  - [ ] `HOST=0.0.0.0`
  - [ ] `CORS_ORIGINS` (update after frontend deployment)
- [ ] Service deployed successfully
- [ ] Health check endpoint responding: `/health`
- [ ] Backend URL noted for frontend configuration

## Frontend Deployment (Vercel)

- [ ] Repository connected to Vercel
- [ ] Project configured with correct settings:
  - [ ] Framework: Vite
  - [ ] Root Directory: `frontend`
  - [ ] Build Command: `npm run build`
  - [ ] Output Directory: `dist`
- [ ] Environment variables set:
  - [ ] `VITE_API_URL` (backend URL from Render)
- [ ] Project deployed successfully
- [ ] Frontend URL noted for CORS configuration

## Post-Deployment

- [ ] Update backend CORS_ORIGINS with frontend URL
- [ ] Test file upload functionality
- [ ] Test question processing
- [ ] Test chart generation
- [ ] Verify error handling
- [ ] Check logs for any issues
- [ ] Set up monitoring/alerts (optional)

## Testing

- [ ] Upload a CSV file
- [ ] Ask a simple question: "What are the column names?"
- [ ] Ask a complex question: "What is the correlation between X and Y?"
- [ ] Test error scenarios (invalid file, malformed questions)
- [ ] Verify charts are generated and displayed
- [ ] Test on different browsers/devices

## Monitoring

- [ ] Backend health check: `https://your-backend.onrender.com/health`
- [ ] Frontend accessibility: `https://your-frontend.vercel.app`
- [ ] Check Render service logs
- [ ] Check Vercel function logs
- [ ] Monitor performance and response times

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Verify CORS_ORIGINS includes frontend URL
   - Check for trailing slashes in URLs
   - Ensure protocol (https/http) matches

2. **Build Failures**
   - Check build logs in platform dashboard
   - Verify all dependencies are listed
   - Test build locally first

3. **Runtime Errors**
   - Check service logs
   - Verify environment variables
   - Test with production environment locally

4. **Slow Response Times**
   - Render free tier sleeps after 15 minutes
   - Consider upgrading to paid tier
   - Implement keep-alive pings if needed

### Rollback Plan

If deployment fails:
1. Check platform logs for errors
2. Revert to previous working commit
3. Redeploy from known good state
4. Fix issues in development branch
5. Test thoroughly before redeploying

## Security Checklist

- [ ] No sensitive data in repository
- [ ] Environment variables properly configured
- [ ] CORS origins restricted to known domains
- [ ] Rate limiting configured
- [ ] File upload restrictions in place
- [ ] Input validation working
- [ ] Error messages don't expose sensitive information

## Performance Checklist

- [ ] Frontend bundle size optimized
- [ ] Images and assets optimized
- [ ] API response times acceptable
- [ ] Database queries optimized (if applicable)
- [ ] Caching configured where appropriate
- [ ] CDN configured for static assets

## Documentation

- [ ] Update README with deployment URLs
- [ ] Document any deployment-specific configuration
- [ ] Update API documentation if endpoints changed
- [ ] Create user guide for the deployed application