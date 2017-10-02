API
===

This page describes module API with detailed explanations of the functions
parameters.

.. module:: aiohttp_jinja2
.. highlight:: python


.. function:: setup(app, *args, app_key=APP_KEY, context_processors=(),
                    filters=None, default_helpers=True, **kwargs)

   Function responsible for initializing templating system on application. This
   one is required to be called first in order to start using this package with
   your application.

   :param app: :class:`aiohttp.web.Application` instance to initialize template
               system on.

   :param str app_key: key that will be used to access templating environment
                       from application dictionary object.

   :param context_processors: list of :ref:`aiohttp-web-middlewares`. These are
                              context processors used to rewrite or inject some
                              variables during the processing of a request.
   :type context_processors: :class:`list`

   :param filters: desc.
   :type filters: :class:`list`

   :param bool default_helpers: whether to use default global helper in
                                templates provided by package
                                :mod:`aiohttp_jinja2.helpers` or not.

   :param ``*args``: positional arguments passed into environment constructor.
   :param ``**kwargs``: any arbitrary keyword arguments you want to pass to
                        :class:`jinja2.Environment` environment.

Example of usage
^^^^^^^^^^^^^^^^
Simple initialization::

   import jinja2
   import aiohttp_jinja2
   from aiohttp import web


   app = web.Application()
   aiohttp_jinja2.setup(
      app,
      loader=jinja2.FileSystemLoader('/path/to/templates/folder'),
   )


.. function:: render_string(template_name, request, context, *,
                            app_key=APP_KEY)

   Renders template specified and returns resulting string.

   :param str template_name: Name of the template you want to render. Usually
                             it's a filename without extension on your
                             filesystem.
   :param request: request to the main application that implies template
                   rendering.
   :type request: :class:`aiohttp.web.Request`

   :param context: set of variables that are used to fill the template.
   :param str app_key: is an optional key for application dict.


.. function:: render_template(template_name, request, context, *,
                              app_key=APP_KEY, encoding='utf-8', status=200)

   :param str template_name: Name of the template you want to render.
   :param request: request to the main application that implies template
                   rendering.
   :type request: :class:`aiohttp.web.Request`

   :param dict context: set of variables that are used to fill the template.
   :param app_key: is an optional key for application dict.
   :param int status: desc.


Example of usage
^^^^^^^^^^^^^^^^
Assuming the initialization from the example about has been done::

   async def handler(request):
      context = {'foo': 'bar'}
      response = aiohttp_jinja2.render_template('tmpl.jinja2',
                                                request,
                                                context)
      return response

   app.router.add_get('/tmpl', handler)

