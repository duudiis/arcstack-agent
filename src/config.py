from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    agent_token: str
    ws_url: str = "http://localhost:4000"
    workspace_dir: str = "/home/arcagent/workspace"
    log_level: str = "INFO"
    heartbeat_interval: int = 30
    command_timeout: int = 30
    max_output_size: int = 65536

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore
