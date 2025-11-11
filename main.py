import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import admin, analysis

app = FastAPI(
    title="Buckminster Fullerene Backend",
    description="The central server for managing users and analyzing screen captures.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, tags=["Client"])
app.include_router(admin.router, tags=["Admin"])


@app.get("/", tags=["Root"])
async def read_root():
    """A simple endpoint to check if the server is running."""
    return {"message": "A.S.T.R.A. Console Backend is online and operational."}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)