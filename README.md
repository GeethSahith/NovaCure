# 🏥 NovaCure Pharmacy Platform

### Prerequisites
1. Python 3.10+
2. A free Supabase Project
3. A free Bytez API Key

### 1. Database Setup
1. Go to your Supabase Dashboard.
2. Open the SQL Editor and paste/run the entire contents of `backend/supabase_setup.sql`. This will magically provision the 6 tables and bind all security triggers.

### 2. Environment Variables
In the `backend/` directory, create a `.env` file replacing standard placeholders:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=ey...
SUPABASE_SERVICE_ROLE_KEY=ey...
SUPABASE_JWT_SECRET=your-secret...
BYTEZ_API_KEY=your-bytez-key
DEBUG=true
```

### 3. Start the Backend Server
```bash
cd backend
python -m venv venv
source venv/Scripts/activate # On Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Boot the Frontend
```bash
cd frontend
python -m http.server 3000
```
Open `http://localhost:3000/index.html` in the browser

