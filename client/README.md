# OPD Claim Adjudication System - Frontend

A modern, beautiful React + TypeScript frontend for the OPD Claim Adjudication System featuring a sophisticated **creamy white and glossy red** design.

## 🎨 Features

- **Claim Submission** - Intuitive form with drag-and-drop file upload
- **Claims Dashboard** - Interactive stats and filterable claims list  
- **Claim Details** - Comprehensive view with decision reasoning
- **Premium Design** - Creamy white background with glossy red accents
- **Smooth Animations** - Fade-in, slide-in, and hover effects
- **Type-Safe** - Full TypeScript implementation
- **Responsive** - Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Prerequisites
- Node.js 18 or higher
- Backend server running on port 8000

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open http://localhost:3000 in your browser.

### Production Build

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ClaimDetails.tsx # Detailed claim viewer
│   │   ├── ClaimsList.tsx   # Dashboard with stats
│   │   ├── FileUpload.tsx   # Drag-and-drop upload
│   │   ├── StatusBadge.tsx  # Glossy status badges
│   │   ├── SubmitClaim.tsx  # Claim submission form
│   │   └── Toast.tsx        # Notifications
│   ├── services/
│   │   └── api.ts           # Backend API integration
│   ├── types/
│   │   └── index.ts         # TypeScript type definitions
│   ├── App.tsx              # Main app with routing
│   ├── index.css            # Design system & styles
│   └── main.tsx             # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 🔌 Backend Integration

The frontend connects to the backend API via Vite proxy:

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Proxy**: `/api` → `http://localhost:8000/api`

All API calls are handled by `src/services/api.ts` with full TypeScript types.

## 🎨 Design System

### Color Palette

- **Cream**: `#FFF8F0` - Primary background
- **Red**: `#DC2626` - Primary accent, CTAs
- **White**: `#FFFFFF` - Cards, inputs
- **Gray**: `#6B7280` - Text, borders

### Typography

- **Font**: Inter (Google Fonts)
- **Sizes**: 0.75rem to 4rem scale

### Components

All components follow the glossy red theme with:
- Gradient backgrounds
- Inset highlights for 3D effect
- Smooth transitions
- Hover states

## 📚 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

## 🛠️ Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client

## 📸 Screenshots

See the [walkthrough document](../IMPLEMENTATION_SUMMARY.md) for detailed screenshots and demos.

## 🤝 Backend Integration

Ensure the backend is running before starting the frontend:

```bash
# In backend directory
cd ../backend
python run.py
```

Then start the frontend:

```bash
# In frontend directory
npm run dev
```

## 🎯 Key Components

### SubmitClaim
- Member selection
- Date picker
- File upload with drag-and-drop
- Form validation

### ClaimsList  
- Statistics cards
- Status filters
- Claims grid
- Empty states

### ClaimDetails
- Claim information
- Decision details
- Confidence score meter
- Document viewer

## 📝 Notes

- The frontend uses Vite's proxy to avoid CORS issues
- All API responses are typed with TypeScript interfaces
- Components are designed mobile-first
- Toast notifications provide user feedback
- Status badges are color-coded for quick recognition

## 🚀 Deployment

Build the production bundle:

```bash
npm run build
```

The `dist/` directory can be deployed to any static hosting service:
- Vercel
- Netlify  
- AWS S3 + CloudFront
- GitHub Pages

---

**Built with ❤️ using React, TypeScript, and Vite**
