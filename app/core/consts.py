from dataclasses import dataclass


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


@dataclass
class PromptTemplate:
    articles_text: str

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