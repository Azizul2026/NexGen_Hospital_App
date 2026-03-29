from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    # Neo4j
    neo4j_uri: str = "neo4j+s://a59e72db.databases.neo4j.io"
    neo4j_username: str = "a59e72db"
    neo4j_password: str = "7OM21aWHFYmmWFHHgD6xQ0gwm7Bkhe5NB7iM2NZYz5c"

    # JWT
    jwt_secret: str = "NexGenHospitalSuperSecretKey2024"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS
    cors_origins: str = '["http://localhost:3000","http://127.0.0.1:5500","http://localhost:8000"]'

    def get_cors_origins(self) -> List[str]:
        try:
            return json.loads(self.cors_origins)
        except Exception:
            return ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
