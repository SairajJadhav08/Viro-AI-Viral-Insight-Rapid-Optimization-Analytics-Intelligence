# Viro-AI Backend

FastAPI backend server for Viro-AI - Viral Insight Rapid Optimization Analytics Intelligence.

## Features

- **Authentication**: JWT-based authentication with user registration and login
- **Project Management**: Create, read, update, and delete projects with file uploads
- **ML Integration**: Integration with mutation predictor, drug analyzer, binding affinity predictor, and chemical modifier
- **Results API**: Comprehensive results endpoints for mutations, drugs, and modifications
- **File Processing**: Support for PDB, FASTA, and CSV file formats
- **Background Processing**: Async processing of projects with status tracking

## Setup

### Prerequisites

- Python 3.9+
- SQLite database (already exists at `Viroai_DataBase/viroai.db`)

### Installation

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file (optional, uses defaults if not present):
```bash
cp .env.example .env
```

4. Update `.env` with your configuration if needed.

### Running the Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python -m app.main
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Projects

- `GET /api/projects` - List projects (with pagination)
- `POST /api/projects` - Create new project (with file uploads)
- `GET /api/projects/{id}` - Get project details
- `PATCH /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `GET /api/projects/{id}/status` - Get processing status

### Results

- `GET /api/projects/{id}/results` - Get complete results
- `GET /api/projects/{id}/mutations` - Get mutation results
- `GET /api/projects/{id}/drugs` - Get drug candidate results
- `GET /api/projects/{id}/modifications` - Get modification results

### Health

- `GET /health` - Health check endpoint

## File Uploads

Supported file types:
- **Protein files**: `.pdb`, `.fasta`, `.fa`
- **Clinical files**: `.csv`, `.tsv`
- **Assay files**: `.csv`, `.tsv`, `.xlsx`

Files are stored in `uploads/projects/{project_id}/{file_type}/`

## ML Models

The backend integrates with the following ML models from the `models/` directory:

1. **EnhancedMutationPredictor** - Predicts viral mutations with 9-section analysis
2. **EnhancedDrugAnalyzer** - Analyzes drug candidates with 11-section analysis
3. **BindingAffinityPredictor** - Predicts drug-virus binding affinity
4. **EnhancedChemicalModifier** - Suggests chemical modifications with 11-section analysis

## Processing Flow

1. User uploads files → Files are saved → Project created with "Pending" status
2. Background task starts processing
3. Files are parsed (PDB/CSV/FASTA)
4. ML models are called:
   - Mutation predictor → Generates mutation predictions
   - Drug analyzer → Analyzes drug candidates
   - Binding affinity predictor → Ranks drugs
   - Chemical modifier → Suggests modifications
5. Results are stored in database
6. Deadliness score is calculated
7. Project status updated to "Completed"

## Database

The backend uses the existing SQLite database at `Viroai_DataBase/viroai.db`. The schema includes:

- `users` - User accounts
- `user_settings` - User preferences
- `projects` - Project metadata
- `mutation_results` - Mutation predictions (9 sections)
- `drug_candidate_results` - Drug analysis (11 sections)
- `modification_results` - Modification suggestions (11 sections)

## Configuration

Key configuration options in `.env`:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `UPLOAD_DIR` - Directory for file uploads
- `MODEL_DIR` - Directory containing ML models
- `CORS_ORIGINS` - Allowed CORS origins

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   ├── core/                # Core utilities (auth, security)
│   └── services/           # Business logic (ML, processing, files)
├── requirements.txt
├── .env.example
└── README.md
```

### Testing

Test the API using the interactive docs at `/docs` or with curl:

```bash
# Register a user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

## Notes

- The backend expects the frontend to be running on `http://localhost:5173` (Vite default)
- File uploads are stored locally. For production, consider using S3 or similar
- ML models are loaded on startup. Ensure model files exist in `models/saved_models/`
- Background processing uses FastAPI's BackgroundTasks. For production, consider Celery

## License

See main project license.

