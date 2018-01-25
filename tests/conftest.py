import pytest
import jinja2
import aiohttp_jinja2
from aiohttp import web


@pytest.fixture()
def app_with_template(loop):
    def aiohttp_app(template):
        app = web.Application(loop=loop)
        aiohttp_jinja2.setup(
            app,
            loader=jinja2.DictLoader({
                'tmpl.jinja2': template
            }),
            enable_async=True,
         )
        return app

    return aiohttp_app
