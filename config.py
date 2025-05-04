from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    # --- API keys ---
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    # huggingface_token: str = Field(..., env="HUGGINGFACE_TOKEN")
    twilio_account_sid: str | None = Field(None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = Field(None, env="TWILIO_AUTH_TOKEN")

    TARGET_EMAIL: str = Field(..., env="TARGET_EMAIL")
    # TARGET_EMAIL = "eliahu1998@gmail.com"
    FROM_EMAIL: str = Field(..., env="FROM_EMAIL")
    EMAIL_PASSWORD: str = Field(..., env="EMAIL_PASSWORD")

    # --- Paths ---
    agent_dir: Path = Field(default=BASE_DIR / "agent")
    business_profile_dir: Path = Field(default=BASE_DIR / "agent" / "business_profile.json")

    data_dir: Path = BASE_DIR / "data"
    user_dir: Path = data_dir / "{costumer_number}"

    lead_template: str = "lead_{costumer_number}.jsonl"  # data_dir / user_dir / "lead_{costumer_number}.jsonl"
    chat_template: str = "chat_log_{costumer_number}.json"  # data_dir / user_dir / "chat_log_{costumer_number}.json"

    logs_dir: Path = data_dir / user_dir / "logs"
    log_lead_template: Path = logs_dir / "deleted_lead_info_{costumer_number}.jsonl"
    log_chat_template: Path = logs_dir / "deleted_chat_{costumer_number}.jsonl"

    # --- Bot params ---
    gpt_model: str = "gpt-4o"
    temperature: float = 0.3

    @field_validator("agent_dir", "business_profile_dir", mode="before")
    @classmethod
    def convert_to_path(cls, v):
        return Path(v) if not isinstance(v, Path) else v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
