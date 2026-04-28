from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import json
from fairness_engine import FairnessEngine
from workflow import run_fairness_analysis

app = FastAPI(title="FairLens API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = FairnessEngine()

# In-memory storage
data_store = {}
history = []

@app.get("/")
def read_root():
    return {"message": "Welcome to the Unbiased AI Decision API"}

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV.")
    
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    # Store data with a simple session ID (using filename for demo)
    session_id = file.filename
    data_store[session_id] = df
    
    sensitive_attrs = engine.detect_sensitive_attributes(df)
    columns = df.columns.tolist()
    
    return {
        "session_id": session_id,
        "columns": columns,
        "detected_sensitive": sensitive_attrs,
        "row_count": len(df),
        "preview": df.head(5).to_dict(orient='records')
    }

@app.post("/analyze")
async def analyze_bias(
    session_id: str = Form(...),
    target_col: str = Form(...),
    sensitive_col: str = Form(...)
):
    if session_id not in data_store:
        raise HTTPException(status_code=404, detail="Session not found. Please upload the dataset again.")
    
    df = data_store[session_id]
    
    if target_col not in df.columns or sensitive_col not in df.columns:
        raise HTTPException(status_code=400, detail="Columns not found in dataset.")
    
    # Delegate entirely to the Mistral AI agent workflow
    report = run_fairness_analysis(df, session_id, target_col, sensitive_col)
    
    if "error" in report:
        raise HTTPException(status_code=500, detail=report["error"])
        
    history.append(report)
    return report

@app.get("/history")
async def get_history():
    return history

@app.get("/demo-dataset")
async def get_demo_dataset():
    # Create a synthetic biased dataset for hiring
    data = {
        'gender': ['Male']*60 + ['Female']*40,
        'experience': np.random.randint(1, 15, 100),
        'education_level': np.random.randint(1, 5, 100),
        'hired': [1]*45 + [0]*15 + [1]*10 + [0]*30 # 75% male hire rate, 25% female hire rate
    }
    df = pd.DataFrame(data)
    session_id = "demo_hiring_data"
    data_store[session_id] = df
    
    return {
        "session_id": session_id,
        "columns": df.columns.tolist(),
        "detected_sensitive": ["gender"],
        "row_count": len(df),
        "preview": df.head(5).to_dict(orient='records')
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
