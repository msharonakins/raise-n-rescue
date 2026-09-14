from fastapi import FastAPI


app = FastAPI(title="Raise 'n Rescue API")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}