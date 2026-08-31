from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    WEBHOOK_SECRET: str = "supersecretkey123"
    GIT_REPO_URL: str = "https://github.com/example/mini-gitops-manifests.git"
    REPO_BRANCH: str = "main"
    LOCAL_REPO_DIR: str = "/tmp/gitops-repo"
    HEALTHCHECK_TIMEOUT_SEC: int = 30
    HEALTHCHECK_INTERVAL_SEC: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()