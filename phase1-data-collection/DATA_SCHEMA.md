# Data Schema Documentation

## Phase 1: Data Collection & Storage

### Overview
This document describes the schema for raw Spotify review data collected from Google Play Store.

---

## Review Data Schema

### JSON Structure
Each review is stored as a JSON object with the following fields:

```json
{
  "review_id": "string",
  "user_name": "string",
  "user_image": "string",
  "content": "string",
  "score": "integer",
  "thumbs_up_count": "integer",
  "review_created_version": "string",
  "at": "string (ISO 8601)",
  "reply_content": "string or null",
  "replied_at": "string (ISO 8601) or null",
  "app_version": "string",
  "collected_at": "string (ISO 8601)"
}
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `review_id` | string | Unique identifier for the review | "gp:AOqpTOH..." |
| `user_name` | string | Display name of the reviewer | "John Doe" |
| `user_image` | string | URL to user's profile image | "https://..." |
| `content` | string | The actual review text | "Great app but..." |
| `score` | integer | Rating given by user (1-5) | 4 |
| `thumbs_up_count` | integer | Number of helpful votes | 12 |
| `review_created_version` | string | App version when review was written | "8.8.96.540" |
| `at` | string (ISO 8601) | Timestamp when review was posted | "2024-01-15T10:30:00Z" |
| `reply_content` | string or null | Developer's response to review | "Thanks for..." |
| `replied_at` | string (ISO 8601) or null | Timestamp of developer reply | "2024-01-16T14:20:00Z" |
| `app_version` | string | Current app version at collection time | "8.8.96.540" |
| `collected_at` | string (ISO 8601) | Timestamp when data was collected | "2024-06-22T22:59:00Z" |

---

## App Information Schema

### JSON Structure
App metadata is stored separately with the following fields:

```json
{
  "title": "string",
  "description": "string",
  "score": "float",
  "ratings": "integer",
  "reviews": "integer",
  "installs": "string",
  "version": "string",
  "updated": "string",
  "category": "string",
  "developer": "string"
}
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | string | App name | "Spotify: Music and Podcasts" |
| `description` | string | App description from store | "Spotify is the best way..." |
| `score` | float | Overall app rating (1-5) | 4.5 |
| `ratings` | integer | Total number of ratings | 50000000 |
| `reviews` | integer | Total number of reviews | 2000000 |
| `installs` | string | Install count range | "1,000,000,000+" |
| `version` | string | Current app version | "8.8.96.540" |
| `updated` | string | Last update date | "2024-01-10" |
| `category` | string | App category | "Music & Audio" |
| `developer` | string | Developer name | "Spotify AB" |

---

## File Naming Convention

### Raw Data Files
- Format: `spotify_reviews_raw_YYYYMMDD_HHMMSS.json`
- Example: `spotify_reviews_raw_20240622_225900.json`
- Location: `data/raw/`

### App Info Files
- Format: `spotify_app_info_YYYYMMDD_HHMMSS.json`
- Example: `spotify_app_info_20240622_225900.json`
- Location: `data/raw/`

---

## Data Quality Considerations

### Expected Data Characteristics
- **Total Reviews**: ~10,000 reviews
- **Language**: Primarily English (may include other languages)
- **Rating Distribution**: Skewed toward higher ratings (typical for popular apps)
- **Time Range**: Most recent reviews (prioritized by sort order)
- **Content Length**: Variable (from short comments to detailed feedback)

### Potential Data Issues
- **Duplicate Reviews**: Same review may appear multiple times
- **Spam**: Some reviews may be automated or low-quality
- **Non-English Content**: May need language filtering in Phase 2
- **Empty Content**: Some reviews may have no text (only rating)
- **Special Characters**: Emojis and unicode characters present

### Handling Strategy
These issues will be addressed in **Phase 2: Data Preprocessing & Cleaning**

---

## Storage Format

### JSON Format
- Encoding: UTF-8
- Indentation: 2 spaces
- Ensure ASCII: False (preserves unicode characters)
- Structure: Array of review objects

### Example File Structure
```json
[
  {
    "review_id": "gp:AOqpTOH...",
    "user_name": "User123",
    "content": "Great app!",
    ...
  },
  {
    "review_id": "gp:AOqpTOI...",
    "user_name": "User456",
    "content": "Needs improvement",
    ...
  }
]
```

---

## Database Schema (Future)

For Phase 4+ when using SQLite/PostgreSQL:

### Reviews Table
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id VARCHAR(255) UNIQUE NOT NULL,
    user_name VARCHAR(255),
    user_image TEXT,
    content TEXT,
    score INTEGER CHECK (score >= 1 AND score <= 5),
    thumbs_up_count INTEGER DEFAULT 0,
    review_created_version VARCHAR(50),
    at TIMESTAMP,
    reply_content TEXT,
    replied_at TIMESTAMP,
    app_version VARCHAR(50),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### App Info Table
```sql
CREATE TABLE app_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255),
    description TEXT,
    score FLOAT,
    ratings INTEGER,
    reviews INTEGER,
    installs VARCHAR(50),
    version VARCHAR(50),
    updated DATE,
    category VARCHAR(100),
    developer VARCHAR(255),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Data Access Patterns

### Reading Data
- Load entire JSON file into memory for analysis
- Use streaming for very large datasets (if needed)

### Writing Data
- Append new reviews to existing dataset (incremental updates)
- Maintain separate files for different collection runs

### Indexing
- `review_id` - Unique identifier for deduplication
- `at` - For time-based analysis
- `score` - For rating-based filtering

---

## Privacy & Compliance

### Data Sensitivity
- User names are public on Google Play Store
- User images are public profile pictures
- Review content is publicly available
- No personal contact information is collected

### Usage Guidelines
- Data is for analysis purposes only
- Do not expose individual user identities
- Aggregate insights for reporting
- Respect Google Play Store Terms of Service
