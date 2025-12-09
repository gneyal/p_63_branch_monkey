"""Main application module."""
from fastapi import FastAPI

app = FastAPI(title="Example App")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"status": "ok"}
