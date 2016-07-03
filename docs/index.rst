.. aiohttp_jinja2 documentation master file, created by
   sphinx-quickstart on Sun Mar 22 12:04:15 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

aiohttp_jinja2
==============

.. module:: aiohttp_jinja2
.. currentmodule:: aiohttp_jinja2
.. highlight:: python

:term:`jinja2` template renderer for :ref:`aiohttp.web<aiohttp-web>`.


Usage
-----

Before template rendering you have to setup *jinja2 environment*
(:class:`jinja2.Environment`) first::

    app = web.Application()
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader('/path/to/templates/folder'))


After that you may use template engine in your
:term:`web-handlers<web-handler>`. The most convenient way is to
decorate a :term:`web-handler`.

Using the function based web handlers::

    @aiohttp_jinja2.template('tmpl.jinja2')
    def handler(request):
        return {'name': 'Andrew', 'surname': 'Svetlov'}

Or the class-based views (:class:`aiohttp.web.View`)::

    class Handler(web.View):
        @aiohttp_jinja2.template('tmpl.jinja2')
        async def get(self):
            return {'name': 'Andrew', 'surname': 'Svetlov'}

On handler call the :func:`template` decorator will pass
returned dictionary ``{'name': 'Andrew', 'surname': 'Svetlov'}`` into
template named ``"tmpl.jinja2"`` for getting resulting HTML text.

If you need more complex processing (set response headers for example)
you may call :func:`render_template` function.

Using a function based web handler::

    async def handler(request):
        context = {'name': 'Andrew', 'surname': 'Svetlov'}
        response = aiohttp_jinja2.render_template('tmpl.jinja2',
                                                  request,
                                                  context)
        response.headers['Content-Language'] = 'ru'
        return response

Or, again, a class-based view (:class:`aiohttp.web.View`)::

    class Handler(web.View):
        async def get(self):
            context = {'name': 'Andrew', 'surname': 'Svetlov'}
            response = aiohttp_jinja2.render_template('tmpl.jinja2',
                                                      self.request,
                                                      context)
            response.headers['Content-Language'] = 'ru'
            return response

Context processors is a way to add some variables to each
template context. It works like :attr:`jinja2.Environment().globals`,
but calculate variables each request. So if you need to
add global constants it will be better to use
:attr:`jinja2.Environment().globals` directly. But if you variables depends of
request (e.g. current user) you have to use context processors.

Context processors is following last-win strategy.
Therefore a context processor could rewrite variables delivered with
previous one.

In order to use context processors create required processors::

    async def foo_processor(request):
        return {'foo': 'bar'}

And pass them into :func:`setup`::

    aiohttp_jinja2.setup(
        app,
        context_processors=[foo_processor,
                            aiohttp_jinja2.request_processor],
        loader=loader)

As you can see, there is a built-in :func:`request_processor`, which
adds current :class:`aiohttp.web.Request` into context of templates
under ``'request'`` name.

By default there are two aiohttp specific :attr:`jinja2.Environment().globals` available in templates:

- ``url``: Resolve a named route url
- ``app``: Use any properties on the app instance

    <body>
        <h1>Welcome to {{ app['name'] }}</h1>
        <a href="{{ url('index') }}">Index Page</a>
    </body>


Library Installation
--------------------

The :mod:`aiohttp_jinja2` can be installed by pip::

   $ pip3 install aiohttp_jinja2

Source code
-----------

The project is hosted on `GitHub <https://github.com/aio-libs/aiohttp_jinja2>`_.

Please feel free to file an issue on `bug tracker
<https://github.com/aio-libs/aiohttp_jinja2/issues>`_ if you have found a bug
or have some suggestion for library improvement.

The library uses `Travis <https://travis-ci.org/aio-libs/aiohttp_jinja2>`_ for
Continuous Integration.

IRC channel
-----------

You can discuss the library on Freenode_ at **#aio-libs** channel.

.. _Freenode: http://freenode.net


.. _aiohttp_jinja2-reference:

Reference
---------


.. data:: APP_KEY

   The key name in :class:`aiohttp.web.Application` dictionary,
   ``'aiohttp_jinja2_environment'`` for storing :term:`jinja2`
   environment object (:class:`jinja2.Environment`).

   Usually you don't need to operate with *application* manually, left
   it to :mod:`aiohttp_jinja2` functions.


.. function:: get_env(app, app_key=APP_KEY)

   Return :class:`jinja2.Environment` object which has stored in the
   *app* (:class:`aiohttp.web.Application` instance).

   *app_key* is an optional key for application dict, :const:`APP_KEY`
   by default.


.. function:: render_string(template_name, request, context, *, \
                            app_key=APP_KEY)

   Return :class:`str` which contains template
   *template_name* filled with *context*.

   *request* is a parameter from :term:`web-handler`,
   :class:`aiohttp.web.Request` instance.

   *app_key* is an optional key for application dict, :const:`APP_KEY`
   by default.


.. function:: render_template(template_name, request, context, *, \
                              app_key=APP_KEY, encoding='utf-8')

   Return :class:`aiohttp.web.Response` which contains template
   *template_name* filled with *context*.

   *request* is a parameter from :term:`web-handler`,
   :class:`aiohttp.web.Request` instance.

   *app_key* is an optional key for application dict, :const:`APP_KEY`
   by default.

   *encoding* is response encoding, ``'utf-8'`` by default.

   Returned response has *Content-Type* header set to ``'text/html'``.


.. function:: setup(app, *args, app_key=APP_KEY, **kwargs)

   Initialize :class:`jinja2.Environment` object.

   *app* is :class:`aiohttp.web.Application` instance.

   *args* and *kawargs* are passed into environment constructor.

   *app_key* is an optional key for application dict, :const:`APP_KEY`
   by default.

   The functions is rougly equivalent for::

      def setup(app, *args, app_key=APP_KEY, **kwargs):
          env = jinja2.Environment(*args, **kwargs)
          app[app_key] = env
          return env


.. decorator:: template(template_name, *, app_key=APP_KEY, encoding='utf-8',\
                        status=200)

   Decorate :term:`web-handler` to convert returned :class:`dict`
   context into :class:`aiohtttp.web.Response` filled with
   *template_name* template.

   *app_key* is an optional key for application dict, :const:`APP_KEY`
   by default.

   *encoding* is response encoding, ``'utf-8'`` by default.

   *status* is *HTTP status code* for returned response, *200* (OK) by
   default.

   Returned response has *Content-Type* header set to ``'text/html'``.


License
-------

:mod:`aiohttp_jinja2` is offered under the Apache 2 license.

Glossary
--------

.. if you add new entries, keep the alphabetical sorting!

.. glossary::

   jinja2

       A modern and designer-friendly templating language for Python.

       See http://jinja.pocoo.org/

   web-handler

       An endpoint that returns http response.


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
