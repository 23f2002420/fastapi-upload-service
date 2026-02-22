from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import StringIO

app = FastAPI()

# CORS configuration (portal-friendly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTS = {".csv", ".json", ".txt"}
MAX_SIZE = 59 * 1024  # 59 KB


# Homepage
@app.get("/")
def home():
    return {"message": "FastAPI Upload Service is running!"}


# GET info for /upload (avoids Method Not Allowed)
@app.get("/upload")
def upload_get_info():
    return {
        "message": "Upload endpoint is ready. Use POST to submit your file.",
        "allowed_file_types": [".csv", ".json", ".txt"],
        "max_size_kb": 59,
        "required_header": "X-Upload-Token-4956",
    }


# POST /upload handles file upload
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), x_upload_token_4956: str = Header(None)
):
    # Authentication
    if x_upload_token_4956 != "9xie6i6mtptbi8gm":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # File type validation
    if not file.filename.lower().endswith(tuple(ALLOWED_EXTS)):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # File size validation
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="Payload Too Large")

    await file.seek(0)

    # Non-CSV files
    if not file.filename.lower().endswith(".csv"):
        return {"message": "Valid but not CSV"}

    # CSV processing
    try:
        df = pd.read_csv(StringIO(content.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    # Required columns check
    if "value" not in df.columns or "category" not in df.columns:
        raise HTTPException(status_code=400, detail="Missing required columns")

    return {
        "email": "23f2002420@ds.study.iitm.ac.in",
        "filename": file.filename,
        "rows": len(df),
        "columns": df.columns.tolist(),
        "totalValue": float(df["value"].sum()),
        "categoryCounts": df["category"].value_counts().to_dict(),
    }
