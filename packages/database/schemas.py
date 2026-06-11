from pydantic import BaseModel


class DatabaseSettings(BaseModel):
    HOST: str = "localhost"
    PORT: int = 5432
    USER: str = "local_user"
    DB: str = "local_db"
    PASSWORD: str = "local_password"

    @property
    def URI(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.USER}:{self.PASSWORD}"
            f"@{self.HOST}:{self.PORT}"
            f"/{self.DB}"
        )
