import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

def get_dotenv_file():

    env = os.getenv("ENV", "dev").lower()  # Default to 'dev' if ENV is not set
    print("---------------- ENV -------- ",env )

    if env == "test":
        return ".env.test"
    elif env == "dev":
        return ".env.dev"
    else:
        raise ValueError(f"Unsupported ENV value: {env}. Expected 'dev' or 'test'.")


dotenv_file = get_dotenv_file()
load_dotenv(dotenv_file)
print("----------- dotenv_file----------",dotenv_file)



class Settings(BaseSettings):
    ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        extra="ignore"
    )

    

settings = Settings()
