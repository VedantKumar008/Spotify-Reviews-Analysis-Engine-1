# Phase-Wise Architecture - Spotify Reviews Analysis Engine

## Overview
This document outlines the phased architecture for building an AI-powered review analysis workflow focused on Spotify user reviews from Google Play.

---

## Phase 1: Data Collection & Storage

### Objective
Collect and store ~10,000 real Spotify reviews from Google Play Store.

### Components
- **Data Source**: Google Play Store reviews for Spotify app
- **Storage Format**: JSON/CSV for initial raw data
- **Database**: SQLite or PostgreSQL for structured storage

### Technical Approach
- Use Google Play Store API or web scraping (with proper rate limiting)
- Extract review fields: review text, rating, date, user ID, version
- Store raw data in `data/raw/` directory
- Implement incremental data collection to prioritize recency

### Deliverables
- Raw dataset of ~10,000 reviews
- Data collection script with error handling
- Documentation of data schema

---

## Phase 2: Data Preprocessing & Cleaning

### Objective
Clean the dataset to remove noise, duplicates, spam, and low-value content.

### Components
- **Data Cleaning Pipeline**: Python-based preprocessing
- **Filtering Logic**: Remove duplicates, spam, very short reviews, non-English content
- **Normalization**: Text normalization (lowercase, remove special characters)

### Technical Approach
- Duplicate detection based on review text and user ID
- Spam detection using simple heuristics (repeated patterns, suspicious keywords)
- Language detection to filter non-English reviews
- Minimum length threshold (e.g., 10+ characters)
- Store cleaned data in `data/processed/` directory
- Cache processed dataset for reuse

### Deliverables
- Cleaned dataset ready for analysis
- Data cleaning pipeline script
- Data quality metrics (before/after)

---

## Phase 3: LLM Integration & Analysis

### Objective
Set up AI analysis to generate insights from the cleaned review dataset.

### Components
- **LLM Provider**: OpenAI GPT-4 or similar (API-based)
- **Prompt Engineering**: Design prompts for 6 research questions
- **Batch Processing**: Process reviews in batches to handle token limits
- **Response Parsing**: Extract and format LLM responses

### Technical Approach
- Use OpenAI API or similar for text analysis
- Design system prompts to focus on product insights
- Implement chunking strategy for large dataset
- Create prompt templates for each research question
- Cache LLM responses to avoid redundant API calls
- Implement retry logic for API failures

### Research Questions Prompts
1. Why do users struggle to discover new music?
2. What are the most common frustrations with recommendations?
3. What listening behaviors are users trying to achieve?
4. What causes users to repeatedly listen to the same content?
5. Which user segments experience different discovery challenges?
6. What unmet needs emerge consistently across reviews?

### Deliverables
- LLM integration module
- Prompt templates for 6 questions
- Analysis execution script
- Sample generated insights

---

## Phase 4: Backend API Development

### Objective
Create a backend API to handle workflow execution and serve results.

### Components
- **Web Framework**: FastAPI or Flask (Python)
- **API Endpoints**:
  - `POST /api/run-workflow` - Trigger analysis workflow
  - `GET /api/results` - Retrieve analysis results
  - `GET /api/status` - Check workflow status
- **Task Queue**: Celery or similar for async processing
- **Caching**: Redis or in-memory caching for results

### Technical Approach
- Implement workflow orchestration (ingestion → cleaning → analysis)
- Use async processing for long-running LLM calls
- Store results in database or file-based cache
- Implement rate limiting to prevent abuse
- Add health check endpoint

### API Response Format
```json
{
  "status": "completed",
  "results": {
    "question_1": "concise answer...",
    "question_2": "concise answer...",
    ...
  },
  "metadata": {
    "reviews_analyzed": 10000,
    "processing_time": "45s"
  }
}
```

### Deliverables
- Backend API with workflow orchestration
- API documentation (OpenAPI/Swagger)
- Unit tests for endpoints

---

## Phase 5: Frontend Development

### Objective
Build a clean, professional web interface with landing page and results page.

### Components
- **Frontend Framework**: React or Next.js
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui or similar
- **State Management**: React hooks or Context API

### Landing Page
- Three horizontally aligned workflow boxes:
  - Reviews Ingestion
  - Data Cleaning
  - LLM Analysis
- Prominent "Run Workflow" button
- Clean, minimal design
- No technical details exposed

### Results Page
- Display 6 research questions with AI-generated answers
- Each answer limited to 3-4 lines
- Show metadata (reviews analyzed, processing time)
- "Run Again" button to re-execute workflow
- Loading states during analysis

### Technical Approach
- Single-page application with client-side routing
- Fetch API calls to backend endpoints
- Responsive design for mobile/desktop
- Loading spinners and progress indicators
- Error handling with user-friendly messages

### Deliverables
- Landing page with workflow visualization
- Results page with 6 Q&A pairs
- Responsive design
- Error handling and loading states

---

## Phase 6: Deployment & Infrastructure

### Objective
Deploy the application for public access with a shareable URL.

### Components
- **Hosting Platform**: Vercel, Railway, or similar
- **Database**: Managed PostgreSQL or SQLite
- **Environment Variables**: API keys, database URLs
- **CI/CD**: Automated deployment pipeline

### Technical Approach
- Containerize application with Docker (optional)
- Set up environment variables for sensitive data
- Configure domain and SSL
- Implement monitoring and logging
- Test deployment end-to-end

### Deployment Options
- **Option 1**: Vercel (frontend) + Railway (backend)
- **Option 2**: Render (full-stack)
- **Option 3**: AWS/GCP/Azure cloud services

### Deliverables
- Deployed application with public URL
- Environment configuration documentation
- Deployment guide
- Monitoring setup

---

## Phase 7: Testing & Optimization

### Objective
Ensure reliability, performance, and user experience.

### Components
- **Unit Tests**: Test individual components
- **Integration Tests**: Test workflow end-to-end
- **Performance Optimization**: Cache optimization, API response times
- **User Testing**: Validate UX with mentors/evaluators

### Technical Approach
- Write unit tests for data cleaning, LLM integration, API endpoints
- Implement integration tests for full workflow
- Optimize LLM API calls with caching
- Test with different network conditions
- Gather feedback and iterate

### Deliverables
- Test suite with >80% coverage
- Performance benchmarks
- User feedback report
- Bug fixes and optimizations

---

## Technology Stack Summary

### Backend
- **Language**: Python 3.9+
- **Web Framework**: FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **Task Queue**: Celery (optional)
- **LLM**: OpenAI GPT-4 API

### Frontend
- **Framework**: Next.js 14 (React)
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **HTTP Client**: Axios or Fetch API

### DevOps
- **Version Control**: Git
- **Hosting**: Vercel (frontend) + Railway (backend)
- **Containerization**: Docker (optional)
- **Environment**: dotenv

---

## Project Structure

```
spotify-reviews-analysis/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   ├── routes/
│   │   └── models/
│   ├── services/
│   │   ├── data_collection.py   # Phase 1
│   │   ├── data_cleaning.py     # Phase 2
│   │   └── llm_analysis.py      # Phase 3
│   ├── data/
│   │   ├── raw/                 # Raw reviews
│   │   └── processed/           # Cleaned reviews
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Landing page
│   │   ├── results/
│   │   └── components/
│   ├── public/
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml (optional)
├── README.md
└── Architecture.md
```

---

## Success Metrics

- **Functional**: All 6 research questions answered with data-driven insights
- **Performance**: Workflow execution < 60 seconds
- **UX**: Clean interface, no authentication required
- **Reliability**: 95%+ uptime, error handling for edge cases
- **Deployment**: Public URL accessible and shareable

---

## Timeline Estimate

- Phase 1: 2-3 days (Data collection)
- Phase 2: 1-2 days (Data cleaning)
- Phase 3: 2-3 days (LLM integration)
- Phase 4: 2-3 days (Backend API)
- Phase 5: 3-4 days (Frontend)
- Phase 6: 1-2 days (Deployment)
- Phase 7: 2-3 days (Testing & optimization)

**Total**: 13-20 days
