import uvicorn

from app.api import app as _app

app = _app

if __name__ == '__main__':
    uvicorn.run("app.api:app", host="127.0.0.1", port=8000)
