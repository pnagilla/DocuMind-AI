from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "DocuMind AI"
    APP_VERSION: str = "0.1.0"

    # File upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 20
    ALLOWED_EXTENSIONS: list[str] = [".pdf"]

    # Chunking
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # FAISS
    FAISS_INDEX_PATH: str = "faiss_index"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # LLM
    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    MAX_RETRIEVED_CHUNKS: int = 5

    # Auth
    SECRET_KEY: str = "change-this-to-a-random-secret-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
