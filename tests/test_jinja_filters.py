import jinja2
from aiohttp import web

import aiohttp_jinja2


async def test_jinja_filters(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def index(request):
        return {}

    def add_2(value):
        return value + 2

    app = web.Application()
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.DictLoader({'tmpl.jinja2': "{{ 5|add_2 }}"}),
        filters={'add_2': add_2}
    )

    app.router.add_route('GET', '/', index)
    client = await aiohttp_client(app)

    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert '7' == txt
