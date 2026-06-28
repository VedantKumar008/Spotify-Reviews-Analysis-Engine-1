# Frontend Documentation

## Phase 5: Frontend Development

### Overview
This document describes the frontend implementation for the Spotify Reviews Analysis Engine, including architecture, components, and technical details.

---

## Architecture

### Technology Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React hooks (useState, useEffect)
- **HTTP Client**: Fetch API (built-in)
- **Routing**: Next.js App Router

### Project Structure
```
phase5-frontend/
├── app/
│   ├── layout.tsx          # Root layout with global styles
│   ├── page.tsx            # Landing page (home)
│   ├── results/
│   │   └── page.tsx        # Results page
│   └── globals.css         # Global CSS with Tailwind
├── package.json            # Dependencies
├── tsconfig.json          # TypeScript configuration
├── tailwind.config.ts     # Tailwind CSS configuration
└── next.config.js         # Next.js configuration with API proxy
```

---

## Pages

### 1. Landing Page (`app/page.tsx`)

**Purpose**: Entry point for the application with workflow visualization.

**Features**:
- Header with title and description
- Three horizontally aligned workflow boxes:
  - Reviews Ingestion (green)
  - Data Cleaning (blue)
  - LLM Analysis (purple)
- Prominent "Run Workflow" button
- Loading state during workflow initiation
- Error handling for failed workflow starts

**Components**:
- Workflow visualization cards with icons
- Animated loading spinner
- Progress indicator
- Error message display

**API Integration**:
- POST `/api/run-workflow` to start analysis
- Redirects to results page with workflow ID

**State Management**:
- `isRunning`: Button loading state
- Router navigation to results page

---

### 2. Results Page (`app/results/page.tsx`)

**Purpose**: Display analysis results with real-time progress updates.

**Features**:
- Real-time progress polling (every 2 seconds)
- Loading state with progress bar
- Error state with retry option
- Results display with 6 Q&A pairs
- Analysis summary metadata
- "Run Again" button to restart workflow

**Components**:
- Progress bar with percentage
- Current step display
- Results cards for each question
- Metadata summary (reviews, time, model, tokens)
- Cached result badges

**API Integration**:
- GET `/api/status/{workflowId}` - Poll for workflow status
- GET `/api/results/{workflowId}` - Fetch completed results

**State Management**:
- `loading`: Loading state
- `error`: Error message
- `results`: Analysis results data
- `progress`: Workflow progress (0-100)
- `currentStep`: Current workflow step

**Polling Logic**:
```typescript
useEffect(() => {
  const pollResults = async () => {
    // Fetch status
    const statusResponse = await fetch(`/api/status/${workflowId}`);
    const statusData = await statusResponse.json();
    
    // Update progress
    setProgress(statusData.progress);
    setCurrentStep(statusData.current_step);
    
    // Check completion
    if (statusData.status === "completed") {
      // Fetch results
      const resultsResponse = await fetch(`/api/results/${workflowId}`);
      setResults(await resultsResponse.json());
      setLoading(false);
    } else if (statusData.status === "failed") {
      setError(statusData.error);
      setLoading(false);
    } else {
      // Continue polling
      setTimeout(pollResults, 2000);
    }
  };
  
  pollResults();
}, [workflowId]);
```

---

## Data Models

### WorkflowResult
```typescript
interface WorkflowResult {
  question: string;
  answer: string;
  cached: boolean;
  reviews_analyzed: number;
}
```

### AnalysisResults
```typescript
interface AnalysisResults {
  generated_at: string;
  model_used: string;
  statistics: {
    total_reviews_analyzed: number;
    total_api_calls: number;
    cache_hits: number;
    cache_misses: number;
    total_tokens_used: number;
    analysis_time_seconds: number;
  };
  results: {
    q1: WorkflowResult;
    q2: WorkflowResult;
    q3: WorkflowResult;
    q4: WorkflowResult;
    q5: WorkflowResult;
    q6: WorkflowResult;
  };
}
```

---

## API Integration

### API Proxy
Next.js rewrites API requests to the backend server:

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

This allows the frontend to call `/api/run-workflow` which gets proxied to `http://localhost:8000/api/run-workflow`.

### API Calls

#### Start Workflow
```typescript
const response = await fetch("/api/run-workflow", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    use_cache: true,
    sample_size: 20,
  }),
});
```

#### Get Status
```typescript
const response = await fetch(`/api/status/${workflowId}`);
const data = await response.json();
```

#### Get Results
```typescript
const response = await fetch(`/api/results/${workflowId}`);
const data = await response.json();
```

---

## Styling

### Tailwind CSS Configuration
```typescript
// tailwind.config.ts
const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
    },
  },
  plugins: [],
};
```

### Design System
- **Primary Color**: Green (Spotify brand)
- **Secondary Colors**: Blue, Purple for workflow steps
- **Typography**: System fonts
- **Spacing**: Tailwind default spacing scale
- **Shadows**: Tailwind shadow utilities
- **Rounded Corners**: Rounded-xl for cards, rounded-full for buttons

### Dark Mode
Supports dark mode via CSS variables and Tailwind's `dark:` modifier:
```css
:root {
  --background: #ffffff;
  --foreground: #171717;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #0a0a0a;
    --foreground: #ededed;
  }
}
```

---

## User Experience

### Landing Page UX
- Clear visual hierarchy with title → description → workflow → CTA
- Workflow visualization shows the three-step process
- Instant feedback on button click (loading state)
- Error handling with user-friendly messages

### Results Page UX
- Real-time progress updates during analysis
- Clear loading state with progress bar
- Step-by-step progress indication
- Results displayed in scannable cards
- Metadata summary at top for quick overview
- "Run Again" button for easy re-execution

### Loading States
- **Button Loading**: Spinner + text change
- **Page Loading**: Full-screen spinner with progress bar
- **Step Loading**: Current step text + percentage

### Error Handling
- Network errors displayed to user
- Retry options available
- Graceful degradation
- User-friendly error messages

---

## Performance Considerations

### Optimization Strategies
- Next.js App Router for optimal performance
- Client-side rendering only where needed
- Efficient polling (2-second intervals)
- Minimal bundle size with tree-shaking
- Tailwind CSS for optimized styles

### Bundle Size
- Next.js automatic code splitting
- Dynamic imports for large components
- Minimal external dependencies
- Axios replaced with native fetch

### Caching
- Next.js automatic static optimization
- Browser caching for static assets
- API response caching handled by backend

---

## Accessibility

### Features
- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Screen reader friendly
- High contrast colors
- Responsive design

### Best Practices
- Alt text for images
- Focus states for interactive elements
- Skip to content links
- Proper heading hierarchy
- Color contrast compliance (WCAG AA)

---

## Browser Compatibility

### Supported Browsers
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

### Polyfills
- Next.js includes necessary polyfills
- Fetch API supported in all modern browsers
- ES6+ features supported

---

## Development

### Running Locally
```bash
cd phase5-frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Building for Production
```bash
npm run build
npm start
```

### Environment Variables
No environment variables required for the frontend.
The backend API URL is configured in `next.config.js`.

---

## Integration with Backend

### Prerequisites
- Backend API must be running on `http://localhost:8000`
- Phase 4 (Backend API) must be completed
- CORS must be configured on backend

### API Endpoints Used
- `POST /api/run-workflow` - Start analysis workflow
- `GET /api/status/{workflowId}` - Get workflow status
- `GET /api/results/{workflowId}` - Get analysis results

### Data Flow
1. User clicks "Run Workflow" on landing page
2. Frontend calls POST `/api/run-workflow`
3. Backend starts workflow and returns workflow ID
4. Frontend redirects to results page with workflow ID
5. Frontend polls GET `/api/status/{workflowId}` every 2 seconds
6. When status is "completed", frontend calls GET `/api/results/{workflowId}`
7. Frontend displays results to user

---

## Future Enhancements

### Potential Improvements
1. **WebSocket Support**: Real-time updates instead of polling
2. **Result Export**: Download results as PDF/CSV
3. **History**: View past analysis results
4. **Comparison**: Compare results across time
5. **Advanced Filtering**: Filter results by criteria
6. **Charts**: Visualize statistics with charts
7. **Mobile App**: React Native mobile application
8. **PWA**: Progressive Web App capabilities
9. **Authentication**: User accounts and saved workflows
10. **Custom Questions**: Allow users to add custom questions

### Scalability
- Server-side rendering for SEO
- Static generation for landing page
- Edge deployment with Vercel/Netlify
- CDN for static assets
- Image optimization with Next.js Image component

---

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure backend is running on port 8000
   - Check CORS configuration on backend
   - Verify API proxy configuration in next.config.js

2. **Workflow Not Starting**
   - Check browser console for errors
   - Verify backend API is accessible
   - Check network tab for failed requests

3. **Results Not Loading**
   - Ensure workflow ID is valid
   - Check backend logs for errors
   - Verify workflow completed successfully

4. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check that globals.css is imported
   - Verify Tailwind content paths

---

## Best Practices

1. **Always use TypeScript** for type safety
2. **Keep components small** and focused
3. **Use React hooks** for state management
4. **Implement error boundaries** for error handling
5. **Optimize images** with Next.js Image component
6. **Use semantic HTML** for accessibility
7. **Test on multiple browsers** for compatibility
8. **Monitor performance** with Lighthouse
9. **Use environment variables** for configuration
10. **Write tests** for critical components
