API
===


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
