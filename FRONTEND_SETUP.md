# Frontend Setup Instructions

## Prerequisites
- Node.js (version 18+ recommended - check with `node --version`)
- npm (comes with Node.js)

## Initial Setup
1. Navigate to frontend folder: `cd frontend`
2. Install dependencies: `npm install`
3. **Important**: Ensure Tailwind CSS v3 is installed (v4 causes setup issues)
   ```bash
   # If you see tailwindcss v4.x.x, uninstall and reinstall v3:
   npm uninstall tailwindcss
   npm install -D tailwindcss@^3.4.0 postcss autoprefixer
   npx tailwindcss init -p
4. Start development server: npm run dev
5. Open http://localhost:5173

# Tailwind CSS Setup
✅ Already configured - should work out of the box after npm install

- Config files: tailwind.config.js and postcss.config.js
- CSS directives added to src/index.css
- Content paths configured for React components
## Verify Tailwind is Working
You should see a blue background with white text on the app. If not:
1. Check that src/main.jsx imports './index.css'
2. Restart the dev server: npm run dev

# Deployment
## Production URLs
- Backend (API): surfdata.vercel.app
- Frontend (React App): slapp-frontend.vercel.app
## Vercel Setup
- Backend Project: Deploys Python Flask API from root directory
- Frontend Project: Deploys React app from /frontend directory
- Auto-deployment: Both projects auto-deploy when pushing to master branch
- Preview deployments: Branch pushes create preview URLs for testing
## Deployment Workflow
- Work on feature branch (e.g., deployment-and-mobile-setup)
- Push branch → Vercel creates preview URLs for testing
- Create PR and merge to master → Updates production URLs

# Troubleshooting
- "could not determine executable to run": You likely have Tailwind v4 installed. Follow step 3 above to downgrade to v3.
- Styles not applying: Restart dev server after any config changes
- npm cache issues: Run npm cache clean --force

# Tech Stack
- React 19.1.1
- Vite 7.1.1
- Tailwind CSS 3.4.0
- PostCSS + Autoprefixer

# Notes
- Created: August 8, 2025
- React + Vite setup complete
- Tailwind CSS: ✅ Configured and working
- Deployment: ✅ Separate Vercel projects for frontend/backend