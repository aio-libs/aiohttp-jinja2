aiohttp_jinja2
==============

jinja2_ template renderer for `aiohttp.web`__.


.. _jinja2: http://jinja.pocoo.org

.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html

__ aiohttp_web_


Usage
-----

Before template rendering you have to setup *jinja2 environment* first::

    app = web.Application(loop=self.loop)
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader('/path/to/templates/folder'))


After that you may to use template engine in your *web-handlers*. The
most convinient way is to decorate *web-handler*::

    @aiohttp_jinja2.template('tmpl.jinja2')
    def handler(request):
        return {'name': 'Andrew', 'surname': 'Svetlov'}

On handler call the ``aiohttp_jinja2.template`` decorator will pass
returned dictionary ``{'name': 'Andrew', 'surname': 'Svetlov'}`` into
template named ``tmpl.jinja2`` for getting resulting HTML text.

If you need more complex processing (set response headers for example)
you may call ``render_template`` function::

    @asyncio.coroutine
    def handler(request):
        context = {'name': 'Andrew', 'surname': 'Svetlov'}
        response = aiohttp_jinja2.render_template('tmpl.jinja2',
                                                  request,
                                                  context)
        response.headers['Content-Language'] = 'ru'
        return response

License
-------

``aiohttp_jinja2`` is offered under the Apache 2 license.
