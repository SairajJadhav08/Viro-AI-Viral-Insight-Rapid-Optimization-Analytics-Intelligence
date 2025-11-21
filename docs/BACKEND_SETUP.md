# Viro-AI Backend Setup Guide

## Quick Start

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   python run.py
   # Or
   uvicorn app.main:app --reload
   ```

5. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

## Database

The backend uses the existing SQLite database at `../Viroai_DataBase/viroai.db`.

The database schema is already created. The backend will automatically create tables if they don't exist.

## Environment Variables

Create a `.env` file (optional, defaults are provided):

```env
DATABASE_URL=sqlite:///./Viroai_DataBase/viroai.db
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_STR=/api
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760
MODEL_DIR=models/saved_models
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

## Testing the API

### 1. Register a user:
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 2. Login:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

Save the `access_token` from the response.

### 3. Create a project:
```bash
curl -X POST "http://localhost:8000/api/projects" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "title=Test Project" \
  -F "description=Test description"
```

### 4. Check project status:
```bash
curl -X GET "http://localhost:8000/api/projects/1/status" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Get results:
```bash
curl -X GET "http://localhost:8000/api/projects/1/results" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Troubleshooting

### Database Connection Issues
- Ensure the database file exists at `Viroai_DataBase/viroai.db`
- Check file permissions

### ML Model Loading Issues
- Ensure model files exist in `models/saved_models/`
- Check console output for model loading messages
- Models will fall back to rule-based predictions if not found

### File Upload Issues
- Check `uploads/` directory permissions
- Verify file size is under `MAX_UPLOAD_SIZE`

### CORS Issues
- Update `CORS_ORIGINS` in `.env` to include your frontend URL
- Default includes `http://localhost:5173` (Vite) and `http://localhost:3000` (React)

## Production Considerations

1. **Change SECRET_KEY** - Use a strong, random secret key
2. **Use PostgreSQL** - Replace SQLite with PostgreSQL for production
3. **File Storage** - Use S3 or similar for file storage
4. **Background Jobs** - Replace BackgroundTasks with Celery for production
5. **HTTPS** - Use HTTPS in production
6. **Rate Limiting** - Add rate limiting middleware
7. **Monitoring** - Add logging and monitoring (e.g., Sentry)

