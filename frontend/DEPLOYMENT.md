# Deployment Guide

## Cloudflare Pages Deployment

### Prerequisites
- A Cloudflare account
- Git repository connected to Cloudflare Pages

### Deployment Steps

1. **Connect to Cloudflare Pages**
   - Go to https://dash.cloudflare.com/
   - Navigate to Workers & Pages > Create application > Pages
   - Connect your GitHub/GitLab repository

2. **Configure Build Settings**
   - **Framework preset:** None (or Vite)
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
   - **Root directory:** `frontend`

3. **Environment Variables**
   - No environment variables required for static deployment
   - If connecting to a backend API, set:
     ```
     VITE_API_BASE_URL=https://your-api-endpoint.com
     ```

4. **Deploy**
   - Click "Save and Deploy"
   - Cloudflare Pages will build and deploy your site
   - You'll get a URL like `https://branch-monkey.pages.dev`

### Custom Domain (Optional)

1. Go to your Pages project settings
2. Click "Custom domains"
3. Add your domain (e.g., `branchmonkey.com`)
4. Update DNS records as instructed

### Automatic Deployments

- Every push to your main branch triggers a new deployment
- Pull requests get preview deployments automatically

### Local Build Test

Before deploying, test the build locally:

```bash
cd frontend
npm run build
npm run preview
```

This will build the project and serve it locally to test production behavior.

### Notes

- The `_redirects` file ensures SPA routing works correctly
- All routes redirect to `index.html` with a 200 status
- Static assets are served from the `dist` directory after build
