from pipeline.scraper import fetch_all_feeds
from pipeline.summarizer import generate_newsletter
from pipeline.renderer import render_html
from pipeline.sender import send_emails_to_active_subscribers


async def run():
    print("🚀 Iniciando pipeline da newsletter...")

    print("📡 Coletando artigos...")
    articles = await fetch_all_feeds()

    if not articles:
        print("❌ Nenhum artigo encontrado. Abortando.")
        return
    
    print("✍️ Gerando newsletter com Claude...")
    newsletter = await generate_newsletter(articles)

    print("🎨 Renderizando HTML...")
    html = render_html(newsletter)

    print("📧 Enviando email...")
    await send_emails_to_active_subscribers(newsletter.subject, html)
    
    print("✅ Newsletter enviada com sucesso!")
