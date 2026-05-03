from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Chao mung ban den voi Ebook2LateX!"}
