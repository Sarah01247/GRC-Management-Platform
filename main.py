from fastapi import FastAPI

app = FastAPI(
    title="GRC Management Platform",
    version="1.0"
)


@app.get("/")
def home():
    return {
        "message": "GRC Platform API is running"
    }