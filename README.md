# Spotify Reviews Analysis Engine

An AI-powered system for analyzing Spotify app reviews at scale. The system processes thousands of user reviews using a hybrid approach combining deterministic NLP processing with LLM synthesis to minimize token costs while maintaining high-quality insights.

## Features

- **Large-Scale Processing**: Analyze 5,000+ reviews efficiently
- **Token-Efficient**: Uses deterministic NLP for intermediate processing, LLM only for final synthesis (~98% token reduction)
- **Resumable Workflows**: Checkpoint-based processing allows resuming from failures
- **Intelligent Caching**: Cached insights returned instantly on subsequent runs
- **Production-Ready**: Deployable on Render (backend) and Vercel (frontend)
- **Database-Backed**: SQLite for development, PostgreSQL for production

## Architecture

### Efficient Workflow

The system uses a novel approach to minimize LLM token consumption:

1. **Deterministic Processing**: Reviews are processed using NLP libraries (spaCy, TextBlob, VADER) for:
   - Keyword extraction
   - Sentiment analysis
   - Theme detection
   - Pattern aggregation

2. **LLM Synthesis**: Only 6 LLM calls are made (one per research question) to synthesize the aggregated patterns into final insights

3. **Database Storage**: All intermediate results are stored in a database for:
   - Checkpointing and resumability
   - Caching final insights
   - Production deployment

### Components

- **Phase 2**: Data cleaning pipeline
- **Phase 3**: LLM analysis (legacy, replaced by efficient workflow)
- **Phase 4**: FastAPI backend with efficient workflow
- **Phase 5**: Next.js frontend

## Local Development

### Prerequisites

- Python 3.8+
- Node.js 18+
- Groq API key ([Get one here](https://console.groq.com/))

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Spotify Reviews Analysis Engine-1
   ```

2. **Install Python dependencies**
   ```bash
   cd phase4-backend-api
   pip install -r requirements.txt
   ```

3. **Install Node dependencies**
   ```bash
   cd ../phase5-frontend
   npm install
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Groq API key
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Download spaCy model** (optional, for better keyword extraction)
   ```bash
   python -m spacy download en_core_web_sm
   ```

### Running Locally

1. **Start the backend**
   ```bash
   cd phase4-backend-api
   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend** (in a new terminal)
   ```bash
   cd phase5-frontend
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Production Deployment

### Backend (Render)

1. **Prepare for deployment**
   - Ensure your code is pushed to GitHub
   - Create a PostgreSQL database on Render

2. **Set environment variables on Render**
   ```
   GROQ_API_KEY=your_groq_api_key
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

3. **Deploy**
   - Connect your GitHub repository to Render
   - Select the `phase4-backend-api` directory as root
   - Render will auto-detect the Python project
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. **Prepare for deployment**
   - Ensure your code is pushed to GitHub
   - Update the backend API URL in frontend environment variables

2. **Set environment variables on Vercel**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   ```

3. **Deploy**
   - Connect your GitHub repository to Vercel
   - Select the `phase5-frontend` directory as root
   - Vercel will auto-detect the Next.js project
   - Deploy

## Environment Variables

### Backend (.env)

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./spotify_reviews.db  # For local development
# DATABASE_URL=postgresql://user:password@host:port/database  # For production
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000  # For local development
# NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com  # For production
```

## Database

### Local Development (SQLite)

The system uses SQLite by default for local development. The database file is created automatically on first run.

### Production (PostgreSQL)

For production, use PostgreSQL. Set the `DATABASE_URL` environment variable:

```
postgresql://username:password@hostname:port/database_name
```

The database tables are created automatically on first run using SQLAlchemy.

## Research Questions

The system analyzes reviews to answer these questions:

1. Why do users struggle to discover new music?
2. What are the most common frustrations with recommendations?
3. What listening behaviors are users trying to achieve?
4. What causes users to repeatedly listen to the same content?
5. Which user segments experience different discovery challenges?
6. What unmet needs emerge consistently across reviews?

## API Endpoints

### POST /api/run-workflow
Start a new analysis workflow.

**Request Body:**
```json
{
  "use_cache": true,
  "use_all_reviews": true,
  "sample_size": 20
}
```

**Response:**
```json
{
  "workflow_id": "20240628_123456_789012",
  "status": "pending",
  "message": "Workflow started successfully"
}
```

### GET /api/status/{workflow_id}
Get the status of a running workflow.

### GET /api/results/{workflow_id}
Get the results of a completed workflow.

### GET /api/health
Health check endpoint.

## Troubleshooting

### Backend won't start

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that the port 8000 is not already in use
- Verify the Groq API key is set correctly in `.env`

### Frontend can't connect to backend

- Ensure the backend is running on port 8000
- Check the `NEXT_PUBLIC_API_URL` in frontend environment variables
- Verify CORS is configured correctly in the backend

### Database errors

- For SQLite: Ensure the application has write permissions to the directory
- For PostgreSQL: Verify the `DATABASE_URL` is correct and the database is accessible

### spaCy model not found

- Install the model: `python -m spacy download en_core_web_sm`
- The system will work without it, but keyword extraction will be less accurate

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
