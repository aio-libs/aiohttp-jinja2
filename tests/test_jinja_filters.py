import aiohttp
import aiohttp_jinja2
import asyncio
import jinja2
import pytest


@pytest.mark.run_loop
def test_jinja_filters(create_server, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def index(request):
        return {}

    def add_2(value):
        return value + 2

    app, url = yield from create_server()
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.DictLoader({'tmpl.jinja2': "{{ 5|add_2 }}"}),
        filters={'add_2': add_2}
    )

    app.router.add_route('GET', '/', index)

    resp = yield from aiohttp.request('GET', url, loop=loop)
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '7' == txt
