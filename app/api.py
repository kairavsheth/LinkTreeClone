from fastapi import FastAPI

from app.routes import router

app = FastAPI(docs_url="/demo", redoc_url="/docs", title="Linktree Backend Clone", version="v0.0.1", description='''
### Stack used
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)

## Setup
1. Clone the repository
2. Rename `.env.sample` file to `.env`
3. Run server using uvicorn command or run `main.py`

## Documentation
1. Documentation available on `/docs`
2. Interactive UI for testing is available on `/demo`
''')

app.include_router(router)
