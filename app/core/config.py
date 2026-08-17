from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str

    gemini_model: str = "gemini-3.6-flash"

    embedding_model: str = "all-MiniLM-L6-v2"

    reranker_model: str = (
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )

    top_k_retrieval: int = 20
    top_k_final: int = 5

    chunk_size: int = 1000
    chunk_overlap: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()