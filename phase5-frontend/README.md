# Phase 5: Frontend Development

## Overview
This phase implements the frontend for the Spotify Reviews Analysis Engine using Next.js, TypeScript, and Tailwind CSS. The frontend provides a user-friendly interface for running the analysis workflow and viewing results.

## Components

### Files
- `app/layout.tsx` - Root layout with global styles
- `app/page.tsx` - Landing page with workflow visualization
- `app/results/page.tsx` - Results page with real-time progress updates
- `app/globals.css` - Global CSS with Tailwind
- `package.json` - Dependencies
- `tsconfig.json` - TypeScript configuration
- `tailwind.config.ts` - Tailwind CSS configuration
- `next.config.js` - Next.js configuration with API proxy
- `FRONTEND_DOCUMENTATION.md` - Detailed frontend documentation

## Setup

### Prerequisites
- Node.js 18 or higher
- npm or yarn package manager
- Backend API running on http://localhost:8000 (Phase 4)

### Installation
```bash
cd phase5-frontend
npm install
```

### Running the Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Building for Production
```bash
npm run build
npm start
```

## Features

### Landing Page
- **Workflow Visualization**: Three horizontally aligned boxes showing the analysis workflow
  - Reviews Ingestion (green)
  - Data Cleaning (blue)
  - LLM Analysis (purple)
- **Run Workflow Button**: Prominent CTA to start the analysis
- **Loading State**: Spinner animation during workflow initiation
- **Error Handling**: User-friendly error messages

### Results Page
- **Real-time Progress**: Polls backend every 2 seconds for workflow status
- **Progress Bar**: Visual progress indicator (0-100%)
- **Current Step Display**: Shows current workflow step
- **Results Display**: 6 research questions with AI-generated answers
- **Metadata Summary**: 
  - Reviews analyzed
  - Processing time
  - Model used
  - Tokens consumed
- **Run Again Button**: Easy re-execution of workflow
- **Error Handling**: Retry option for failed workflows

## API Integration

The frontend integrates with the Phase 4 backend API through Next.js API proxy:

### API Endpoints
- `POST /api/run-workflow` - Start analysis workflow
- `GET /api/status/{workflowId}` - Get workflow status
- `GET /api/results/{workflowId}` - Get analysis results

### API Proxy Configuration
```javascript
// next.config.js
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*',
    },
  ]
}
```

## Technology Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React hooks (useState, useEffect)
- **HTTP Client**: Fetch API (built-in)
- **Routing**: Next.js App Router

## Design

### Color Scheme
- **Primary**: Green (Spotify brand)
- **Secondary**: Blue, Purple for workflow steps
- **Background**: Gradient from green-50 to green-100
- **Dark Mode**: Supported via CSS variables

### Typography
- System fonts for optimal performance
- Clear hierarchy with headings
- Readable body text

### Components
- **Workflow Cards**: Rounded-xl with colored borders
- **Buttons**: Rounded-full with hover effects
- **Progress Bar**: Smooth transitions
- **Result Cards**: Left border accent

## User Experience

### Landing Page
1. User sees workflow visualization
2. User clicks "Run Workflow"
3. Button shows loading state
4. Redirects to results page

### Results Page
1. User sees loading state with progress bar
2. Progress updates every 2 seconds
3. When complete, results display automatically
4. User can click "Run Again" to restart

## Performance

- **Optimized Bundle**: Next.js automatic code splitting
- **Efficient Polling**: 2-second intervals for status checks
- **Minimal Dependencies**: Only essential packages
- **Tailwind CSS**: Optimized styles with purging

## Accessibility

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Screen reader friendly
- High contrast colors
- Responsive design

## Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### API Connection Errors
- Ensure backend is running on port 8000
- Check CORS configuration on backend
- Verify API proxy configuration in next.config.js

### Workflow Not Starting
- Check browser console for errors
- Verify backend API is accessible
- Check network tab for failed requests

### Results Not Loading
- Ensure workflow ID is valid
- Check backend logs for errors
- Verify workflow completed successfully

### Styling Issues
- Ensure Tailwind CSS is properly configured
- Check that globals.css is imported
- Verify Tailwind content paths

## Integration with Backend

### Prerequisites
- Backend API must be running on http://localhost:8000
- Phase 4 (Backend API) must be completed
- CORS must be configured on backend

### Data Flow
1. Frontend calls POST /api/run-workflow
2. Backend starts workflow and returns workflow ID
3. Frontend redirects to results page
4. Frontend polls GET /api/status/{workflowId}
5. When complete, frontend calls GET /api/results/{workflowId}
6. Frontend displays results

## Development

### File Structure
```
phase5-frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Landing page
│   ├── results/
│   │   └── page.tsx        # Results page
│   └── globals.css         # Global styles
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

### Adding New Features
1. Create new components in app/ or components/
2. Add pages in app/ directory
3. Update API integration as needed
4. Test with backend running

## Documentation

For detailed technical documentation, see `FRONTEND_DOCUMENTATION.md`.

## Next Steps

After frontend development:
1. Test full pipeline (Phases 1-5)
2. Deploy backend and frontend
3. Proceed to Phase 6 (Deployment) as per Architecture.md

## Notes

- Uses Next.js App Router for optimal performance
- TypeScript for type safety
- Tailwind CSS for rapid development
- API proxy for seamless backend integration
- Real-time progress updates via polling
- Responsive design for all screen sizes
