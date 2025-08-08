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

## Deployment
- [Add Vercel setup steps once we figure them out]

## Notes
- Created: [Today's date]
- React + Vite setup
- Tailwind CSS: Not yet configured (npm issues)