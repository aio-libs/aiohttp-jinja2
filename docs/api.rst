API
===

Describes the module API with detailed explanations of functions parameters.

.. module:: aiohttp_jinja2
.. highlight:: python


APP_KEY
-------

.. data:: APP_KEY

   The key name in :class:`aiohttp.web.Application` dictionary,
   ``'aiohttp_jinja2_environment'`` for storing :term:`jinja2`
   environment object (:class:`jinja2.Environment`).

   Usually you don't need to operate with *application* manually, left
   it to :mod:`aiohttp_jinja2` functions.


setup
-----

.. function:: setup(app, *args, app_key=APP_KEY, context_processors=(), \
                    autoescape=True, \
                    filters=None, default_helpers=True, **kwargs)

   Function responsible for initializing templating system on application. It
   must be called before freezing or running the application in order to use
   *aiohttp-jinja*.

   :param app: :class:`aiohttp.web.Application` instance to initialize template
               system on.

   :param str app_key: optional key that will be used to access templating
                       environment from application dictionary object. Defaults
                       to `aiohttp_jinja2_environment`.

   :param context_processors: list of :ref:`aiohttp-web-middlewares`. These are
                              context processors used to rewrite or inject some
                              variables during the processing of a request.
   :type context_processors: :class:`list`

   :param autoescape: the argument is passed to :class:`jinja2.Environemnt`, see
                           `Autoescaping` for more details.

   :param filters: extra jinja filters (`link to docs
                   <http://jinja.pocoo.org/docs/2.10/templates/#filters>`).
   :type filters: :class:`list`

   :param bool default_helpers: whether to use default global helper in
                                templates provided by package
                                :mod:`aiohttp_jinja2.helpers` or not.

   :param ``*args``: positional arguments passed into environment constructor.
   :param ``**kwargs``: any arbitrary keyword arguments you want to pass to
                        :class:`jinja2.Environment` environment.

   Simple initialization::

      import jinja2
      import aiohttp_jinja2
      from aiohttp import web

      app = web.Application()
      aiohttp_jinja2.setup(
         app,
         loader=jinja2.FileSystemLoader('/path/to/templates/folder'),
      )


@template
--------

.. decorator:: template(template_name, *, app_key=APP_KEY, \
                        encoding='utf-8', status=200)

   Behaves as a decorator around view functions accepting template name that
   should be used to render the response. Supports both synchronous and
   asynchronous functions.

   :param str template_name: name of the template file that will be looked up
                             by the loader. Raises a 500 error in case template
                             was not found.

   :param str app_key: optional key that will be used to access templating
                       environment from application dictionary object. Defaults
                       to `aiohttp_jinja2_environment`.

   :param str encoding: encoding that will be set as a charset property on the
                        response for rendered template, default to utf-8.

   :params int status: http status code that will be set on resulting response.


   Simple usage example::

      @jinja2.template('tmpl.jinja2')
      async def handler(request):
         context = {'foo': 'bar'}
         return context

      app.router.add_get('/tmpl', handler)

render_string
-------------

.. function:: render_string(template_name, request, context, *, \
                            app_key=APP_KEY)

   Renders template specified and returns resulting string.

   :param str template_name: Name of the template you want to render. Usually
                             it's a filename without extension on your
                             filesystem.
   :param request: aiohttp request associated with an application where
                   aiohttp-jinja rendering is configured.
   :type request: :class:`aiohttp.web.Request`

   :param dict context: dictionary used as context when rendering the template.
   :param str app_key: optional key that will be used to access templating
                       environment from application dictionary object. Defaults
                       to `aiohttp_jinja2_environment`.


render_string_async
-------------------

.. function:: render_string_async(template_name, request, context, *, \
                                  app_key=APP_KEY)
    :async:

    Async version of ``render_string()``.

    Replaces ``render_string()`` when ``enable_async=True`` is passed to the
    ``setup()`` call.

    See ``render_string()`` for parameter usage.



render_template
---------------

.. function:: render_template(template_name, request, context, *, \
                              app_key=APP_KEY, encoding='utf-8', status=200)

   :param str template_name: Name of the template you want to render.
   :param request: aiohttp request associated with an application where
                   aiohttp-jinja rendering is configured.
   :type request: :class:`aiohttp.web.Request`

   :param dict context: dictionary used as context when rendering the template.
   :param str app_key: optional key that will be used to access templating
                       environment from application dictionary object. Defaults
                       to `aiohttp_jinja2_environment`.
   :param int status: http status code that will be set on resulting response.

   Assuming the initialization from the example above has been done::

      async def handler(request):
         context = {'foo': 'bar'}
         response = aiohttp_jinja2.render_template('tmpl.jinja2',
                                                request,
                                                context)
         return response

      app.router.add_get('/tmpl', handler)


render_template_async
---------------------

.. function:: render_template_async( \
        template_name, request, context, *, \
        app_key=APP_KEY, encoding='utf-8', status=200)
    :async:

    Async version of ``render_template()``.

    Replaces ``render_template()`` when ``enable_async=True`` is passed to the
    ``setup()`` call.

    See ``render_template()`` for parameter usage.



.. function:: get_env(app, *, app_key=APP_KEY)

   Get aiohttp-jinja2 environment from an application instance by key.

   :param app: :class:`aiohttp.web.Application` instance to get variables from.

   :param str app_key: optional key that will be used to access templating
                           environment from application dictionary object. Defaults
                           to `aiohttp_jinja2_environment`.
