from pydantic import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXP_DELTA_SECONDS: int
    MONGO_DETAILS: str

    class Config:
        env_file = ".env"


settings = Settings()
