from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


RSS_FEEDS: dict[str, str] = {
    # "CaféPoint": "https://www.cafepoint.com.br/",# Criar um scraper para esse
    "Revista Espresso": "https://revistaespresso.com.br/feed/",
    "CeCafé": "https://www.cecafe.com.br/feed/",
    "Revista Cafeicultura": "https://www.revistacafeicultura.com.br/feed/",
    "Blog do Café": "https://www.blogdocafe.com.br/feeds/posts/default?alt=rss",
    "Coffee & Joy Blog": "https://blog.coffeeandjoy.com.br/feed/",
    "r/CafeEspecialBR": "https://www.reddit.com/r/CafeEspecialBR.rss",
    "Perfect Daily Grind": "https://perfectdailygrind.com/feed/",
    "Daily Coffee News": "https://dailycoffeenews.com/feed/",
    "Sprudge": "https://sprudge.com/feed/",
    "Fresh Cup": "https://freshcup.com/feed/",
    "SCA News": "https://sca.coffee/sca-news?format=rss",
    "Barista Magazine": "https://www.baristamagazine.com/feed/",
    "Coffee Chronicler": "https://coffeechronicler.com/feed/",
}

PROMPT: str = """Você é o editor de uma newsletter semanal chamada "Café & Novidades".
Seu público são entusiastas de café especial brasileiros — curiosos, cultos, apaixonados pela bebida.

Abaixo estão artigos coletados de sites especializados em café nesta semana.
Sua tarefa:
1. Selecione os 5-7 artigos mais relevantes e interessantes
2. Escreva um resumo em português de 2-3 frases para cada um (sem copiar o original)
3. Crie um parágrafo de abertura animado e um de encerramento curto
4. Sugira um assunto criativo para o email

Responda APENAS com um JSON válido, sem markdown, sem texto fora do JSON.
Formato exato:
{{
  "subject": "assunto do email aqui",
  "intro": "parágrafo de abertura aqui",
  "week_label": "Semana X · Mês Ano",
  "items": [
    {{
      "title": "título do artigo",
      "source": "nome da fonte",
      "url": "url original",
      "summary": "resumo em português aqui"
    }}
  ],
  "closing": "parágrafo de encerramento aqui"
}}

Artigos desta semana:
{articles_text}"""

HTML:str = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Café & Novidades — {week_label}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: Georgia, serif;
      background: #faf8f3;
      color: #2c1a0e;
      padding: 2rem 1rem;
    }}
    .container {{ max-width: 680px; margin: 0 auto; }}

    header {{
      text-align: center;
      border-bottom: 2px solid #6f3f1e;
      padding-bottom: 1.5rem;
      margin-bottom: 2rem;
    }}
    header h1 {{
      font-size: 2rem;
      color: #6f3f1e;
      letter-spacing: 0.05em;
    }}
    .week-label {{
      color: #9c6644;
      font-size: 0.9rem;
      margin-top: 0.25rem;
    }}

    .intro {{
      background: #fff9f2;
      border-left: 4px solid #c87941;
      padding: 1rem 1.25rem;
      margin-bottom: 2.5rem;
      border-radius: 0 6px 6px 0;
      line-height: 1.7;
    }}

    .item {{
      background: white;
      border-radius: 8px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    }}
    .source {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #9c6644;
      font-family: sans-serif;
    }}
    .item h2 {{
      font-size: 1.15rem;
      margin: 0.4rem 0 0.75rem;
      line-height: 1.4;
    }}
    .item h2 a {{
      color: #2c1a0e;
      text-decoration: none;
    }}
    .item h2 a:hover {{ color: #6f3f1e; text-decoration: underline; }}
    .item p {{ line-height: 1.7; color: #4a3728; margin-bottom: 1rem; }}
    .read-more {{
      font-family: sans-serif;
      font-size: 0.85rem;
      color: #c87941;
      text-decoration: none;
      font-weight: bold;
    }}
    .read-more:hover {{ text-decoration: underline; }}

    .closing {{
      text-align: center;
      margin-top: 2.5rem;
      padding-top: 1.5rem;
      border-top: 1px solid #e0d5c8;
      color: #6b4f3a;
      font-style: italic;
      line-height: 1.7;
    }}

    footer {{
      text-align: center;
      margin-top: 2rem;
      font-family: sans-serif;
      font-size: 0.75rem;
      color: #b0967e;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>☕ Café & Novidades</h1>
      <p class="week-label">{week_label}</p>
    </header>

    <div class="intro">{intro}</div>

    {items_html}

    <div class="closing">{closing}</div>

    <footer>
      <p>Todos os artigos pertencem aos seus respectivos autores e publicações.</p>
      <p>Esta newsletter faz curadoria e resume conteúdo público, sempre com link para a fonte original.</p>
    </footer>
  </div>
</body>
</html>"""


class DatabaseSettings(BaseModel):
    HOST: str = "localhost"
    PORT: int = 5432
    USER: str
    DB: str
    PASSWORD: str

    @property
    def URI(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:"
            f"{self.PASSWORD}@{self.HOST}:"
            f"{self.PORT}/{self.DB}"
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="COFFEE_",
        case_sensitive=True,
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Database
    DATABASE: DatabaseSettings

    # App
    APP_NAME: str = "Coffee Newsletter"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Pipeline
    CLAUDE_MODEL: str = "claude-haiku-4-5-20251001"
    CLAUDE_MAX_TOKENS: int = 2000
    DAYS_BACK: int = 7
    ANTHROPIC_API_KEY: str | None
    RESEND_API_KEY: str | None
    FROM_EMAIL: str | None
    TO_EMAIL: str | None


settings = Settings()
