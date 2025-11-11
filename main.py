# main.py (CORRECTED VERSION)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import admin, analysis

app = FastAPI(
    title="A.S.T.R.A. Backend",
    description="The central server for managing users and analyzing screen captures.",
    version="1.0.0"
)

# !! DEFINE YOUR ACTUAL URLs HERE !!
ASTRA_CONSOLE_URL = "https://astra-console-mahi.vercel.app" # <--- APNA FRONTEND URL DAALO
BACKEND_URL = "https://backend-theta-self-37.vercel.app" # <--- APNA BACKEND URL DAALO

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        ASTRA_CONSOLE_URL, 
        # BACKEND_URL, # Backend URL daalne ki zaroorat nahi hoti usually
        "http://localhost:3000", # Local testing ke liye rakh sakte ho
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)
app.include_router(admin.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "A.S.T.R.A. Console Backend is online and operational."}

# if __name__ == "__main__" block Vercel use nahi karta, so usko chhod do.
