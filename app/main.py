from fastapi import FastAPI

app = FastAPI(title="APISense API")


@app.get("/")
def root():
    return {"message": "APISense Backend is running 🚀"}