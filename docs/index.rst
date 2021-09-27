.. aiohttp_jinja2 documentation master file, created by
   sphinx-quickstart on Sun Mar 22 12:04:15 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

aiohttp_jinja2
==============

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

More complex template processing can be achieved by modifying the existing
`list of global functions <http://jinja.pocoo.org/docs/2.10/templates/#builtin-globals>`_.
Modification of Jinja2's environment can be done via :func:`get_env`.
For example, adding the ``zip`` function::

    env = aiohttp_jinja2.get_env(app)
    env.globals.update(zip=zip)


Which can now to be used in any template::

    {% for value, square in zip(values, squares) %}
        <p>The square of {{ value }} is {{ square }}.</p>
    {% endfor %}


In some cases, finer control over the dataflow may also be required.
This can be worked out by explicitly asking for template to be rendered
using :func:`render_template`.
Explicit rendering will allow to possibly
pass some context to the renderer
and also to modify its response on the fly.
This can for example be used to set response headers::

    async def handler(request):
        context = {'name': 'Andrew', 'surname': 'Svetlov'}
        response = aiohttp_jinja2.render_template('tmpl.jinja2',
                                                  request,
                                                  context)
        response.headers['Content-Language'] = 'ru'
        return response

This, again, can also be done with a class-based view (:class:`aiohttp.web.View`)::

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

Here is an example of how to add current user dependant logic
to template (requires ``aiohttp_security`` library)::

    from aiohttp_security import authorized_userid

    async def current_user_ctx_processor(request):
        userid = await authorized_userid(request)
        is_anonymous = not bool(userid)
        return {'current_user': {'is_anonymous': is_anonymous}}

Template::

    <body>
        <div>
            {% if current_user.is_anonymous %}
                <a href="{{ url('login') }}">Login</a>
            {% else %}
                <a href="{{ url('logout') }}">Logout</a>
            {% endif %}
        </div>
    </body>

Async functions
...............

If you pass the ``enable_async`` parameter to the setup function, then you
will need to use the async functions for rendering::

    aiohttp_jinja2.setup(
        app, enable_async=True,
        loader=jinja2.FileSystemLoader('/path/to/templates/folder'))

    ...

    async def handler(request):
        return await aiohttp_jinja2.render_template_async(
            'tmpl.jinja2', request)

The ``@aiohttp_jinja2.template`` decorator will work for both cases.

Default Globals
...............

.. highlight:: html+jinja

``app`` is always made in templates via :attr:`jinja2.Environment().globals`::

    <body>
        <h1>Welcome to {{ app['name'] }}</h1>
    </body>


Two more helpers are also enabled by default: ``url`` and ``static``.

``url`` can be used with just a view name::

    <body>
        <a href="{{ url('index') }}">Index Page</a>
    </body>


Or with arguments::

    <body>
        <a href="{{ url('user', id=123) }}">User Page</a>
    </body>

A query can be added to the url with the special ``query_`` keyword argument::

    <body>
        <a href="{{ url('user', id=123, query_={'foo': 'bar'}) }}">User Page</a>
    </body>


For a view defined by ``app.router.add_get('/user-profile/{id}/',
user, name='user')``, the above would give::

    <body>
        <a href="/user-profile/123/?foo=bar">User Page</a>
    </body>


This is useful as it would allow your static path to switch in
deployment or testing with just one line.

The ``static`` function has similar usage, except it requires you to
set ``static_root_url`` on the app

.. code-block:: ruby

    app = web.Application()
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader('/path/to/templates/folder'))
    app['static_root_url'] = '/static'

Then in the template::

        <script src="{{ static('dist/main.js') }}"></script>


Would result in::

        <script src="/static/dist/main.js"></script>


Both ``url`` and ``static`` can be disabled by passing
``default_helpers=False`` to ``aiohttp_jinja2.setup``.

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

The library uses `Travis <https://travis-ci.org/aio-libs/aiohttp-jinja2>`_ for
Continuous Integration.


License
-------

:mod:`aiohttp_jinja2` is offered under the Apache 2 license.

Contents
--------

.. toctree::
   :maxdepth: 2

   api


Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`


Glossary
--------

.. if you add new entries, keep the alphabetical sorting!

.. glossary::

   jinja2

       A modern and designer-friendly templating language for Python.

       See http://jinja.pocoo.org/

   web-handler

       An endpoint that returns http response.
