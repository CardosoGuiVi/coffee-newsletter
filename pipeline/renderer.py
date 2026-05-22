from pipeline.schemas.summarizer import Newsletter
from app.core.config import HTML


def render_html(newsletter: Newsletter) -> str:
    items_html = "\n".join([
        f"""
        <article class="item">
          <span class="source">{item.source}</span>
          <h2><a href="{item.url}" target="_blank" rel="noopener">{item.title}</a></h2>
          <p>{item.summary}</p>
          <a class="read-more" href="{item.url}" target="_blank" rel="noopener">
            Ler artigo completo →
          </a>
        </article>
        """
        for item in newsletter.items
    ])

    return HTML.format(
        week_label=newsletter.week_label,
        intro=newsletter.intro,
        items_html=items_html,
        closing=newsletter.closing
    )
