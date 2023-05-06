import os

import google.auth
from google.cloud import secretmanager
from pydantic import BaseSettings

try:
    _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
except google.auth.exceptions.DefaultCredentialsError:
    pass

if os.path.isfile(".env"):
    env = '.env'
elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    # Pull secrets from Secret Manager
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", "linktree_secrets")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    with open('.gcp_env', 'w') as f:
        f.write(payload)
        f.close()

    env = '.gcp_env'
else:
    raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")


class Settings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXP_DELTA_SECONDS: int
    MONGO_DETAILS: str

    class Config:
        env_file = env


settings = Settings()

if os.path.isfile('.gcp_env'):
    os.remove('.gcp_env')
