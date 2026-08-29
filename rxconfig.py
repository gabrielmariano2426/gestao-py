import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin

from gestao_py.config import DATABASE_URL

config = rx.Config(
    app_name="gestao_py",
    db_url=DATABASE_URL,
    disable_plugins=[SitemapPlugin],
)
