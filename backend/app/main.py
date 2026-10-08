from fastapi import FastAPI

from backend.app.api.auth import router as auth_router


app = FastAPI(title="Raise 'n Rescue API")

app.include_router(auth_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}