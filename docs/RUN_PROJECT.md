# Running Viro-AI Project

## ✅ Project Status

Both servers are now running!

---

## 🚀 Running Servers

### **Backend Server** ✅
- **Status:** Running
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Port:** 8000

### **Frontend Server** ✅
- **Status:** Running
- **URL:** http://localhost:5173
- **Port:** 5173

---

## 📋 Quick Start Commands

### **Start Backend:**
```bash
cd backend
python run.py
```

Or with uvicorn directly:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Start Frontend:**
```bash
cd workspace/shadcn-ui
pnpm dev
```

Or with npm:
```bash
cd workspace/shadcn-ui
npm run dev
```

---

## 🔍 Verify Servers Are Running

### **Check Backend:**
```bash
# Check if port 8000 is listening
netstat -ano | findstr ":8000"

# Test health endpoint
curl http://localhost:8000/health
# Or in PowerShell:
Invoke-WebRequest -Uri "http://localhost:8000/health"
```

### **Check Frontend:**
```bash
# Check if port 5173 is listening
netstat -ano | findstr ":5173"

# Open in browser
start http://localhost:5173
```

---

## 🌐 Access Points

### **Backend API:**
- **Base URL:** http://localhost:8000/api
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

### **Frontend:**
- **Application:** http://localhost:5173
- **Hot Reload:** Enabled (changes auto-refresh)

---

## 🧪 Test the Application

### **1. Open Frontend:**
Open your browser and navigate to:
```
http://localhost:5173
```

### **2. Register/Login:**
- Click "Sign Up" to create an account
- Or use existing credentials to sign in

### **3. Create a Project:**
- Navigate to "Create Project"
- Fill in project details
- Upload files (optional):
  - Protein files: `.pdb`, `.fasta`, `.fa`
  - Clinical files: `.csv`, `.tsv`
  - Assay files: `.csv`, `.tsv`, `.xlsx`
- Submit and wait for processing (10-30 seconds)

### **4. View Results:**
- After processing completes, view:
  - Mutations (9-section analysis)
  - Drug Candidates (11-section analysis)
  - Modifications (11-section analysis)
  - Deadliness Score

---

## 🔧 Troubleshooting

### **Backend Not Starting:**
1. Check if port 8000 is already in use:
   ```bash
   netstat -ano | findstr ":8000"
   ```
2. Kill the process if needed:
   ```bash
   taskkill /PID <process_id> /F
   ```
3. Check Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### **Frontend Not Starting:**
1. Check if port 5173 is already in use:
   ```bash
   netstat -ano | findstr ":5173"
   ```
2. Install dependencies:
   ```bash
   cd workspace/shadcn-ui
   pnpm install
   ```
3. Check Node.js version (should be 18+):
   ```bash
   node --version
   ```

### **CORS Errors:**
- Ensure backend CORS settings include frontend URL
- Default: `http://localhost:5173` is already configured
- Check `backend/app/config.py` for CORS_ORIGINS

### **Database Errors:**
- Ensure database exists: `Viroai_DataBase/viroai.db`
- Backend will auto-create tables on first run
- Check file permissions

### **ML Model Errors:**
- Models should be in `models/saved_models/`
- System will fall back to rule-based predictions if models not found
- Check console output for model loading messages

---

## 📊 Server Logs

### **Backend Logs:**
- Check terminal where `python run.py` is running
- Look for:
  - `[ML Service] Mutation predictor loaded`
  - `[ML Service] ML-powered drug analyzer loaded`
  - `[ML Service] Binding affinity predictor loaded`
  - `[ML Service] ML-powered chemical modifier loaded`
  - `Application startup complete`

### **Frontend Logs:**
- Check terminal where `pnpm dev` is running
- Look for:
  - `VITE v5.x.x ready in xxx ms`
  - `➜  Local:   http://localhost:5173/`

---

## 🛑 Stopping Servers

### **Stop Backend:**
- Press `Ctrl+C` in the backend terminal
- Or kill the process:
  ```bash
  taskkill /PID <process_id> /F
  ```

### **Stop Frontend:**
- Press `Ctrl+C` in the frontend terminal
- Or kill the process:
  ```bash
  taskkill /PID <process_id> /F
  ```

---

## ✅ Current Status

**Backend:** ✅ Running on http://localhost:8000  
**Frontend:** ✅ Running on http://localhost:5173

**You can now:**
1. Open http://localhost:5173 in your browser
2. Register/Login
3. Create projects
4. View results

---

**Last Updated:** November 21, 2025  
**Status:** ✅ Both Servers Running

