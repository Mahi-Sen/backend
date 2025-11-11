import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import admin, analysis

app = FastAPI(
    title="Buckminster Fullerene Backend",
    description="The central server for managing users and analyzing screen captures.",
    version="1.0.0"
)

ASTRA_CONSOLE_URL = "https://your-astra-console-url.vercel.app" 

app.add_middleware(
    CORSMiddleware,
    # This is the most important change. We are being specific.
    allow_origins=[
        "http://localhost:3000", # If you run ASTRA locally for testing
        "http://127.0.0.1:3000", # Another local variant
        ASTRA_CONSOLE_URL 
    ],
    allow_credentials=True,
    allow_methods=["*"], # Allows GET, POST, PUT, DELETE, etc.
    allow_headers=["*"], # Allows headers like X-Admin-API-Key
)

app.include_router(analysis.router) # No need for tags here, they can be in the router files
app.include_router(admin.router)

# @app.get("/", tags=["Root"])
# async def read_root():
#     return {"message": "A.S.T.R.A. Console Backend is online and operational."}

@app.get("/", tags=["Root"])
async def read_root():
    """A simple endpoint to check if the server is running."""
    return {"message": "A.S.T.R.A. Console Backend is online and operational."}


if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

