=======
CHANGES
=======

.. towncrier release notes start

1.5.1 (2023-02-01)
==================

- Add support for Python 3.11.
- Drop support for decorating non-async functions with @template (deprecated since 0.16).

1.5 (2021-08-21)
================

- Drop support for jinaj2 <3. Add support for 3+.
- Don't require ``typing_extensions`` on Python 3.8+.

1.4.2 (2020-11-23)
==================

- Add CHANGES.rst to MANIFEST.in and sdist #402

1.4.1 (2020-11-22)
==================

- Document async rendering functions #396

1.4.0 (2020-11-12)
==================

- Fix type annotation for ``context_processors`` argument #354

- Bump the minimal supported ``aiohttp`` version to 3.6.3 to avoid problems
  with uncompatibility between ``aiohttp`` and ``yarl``

- Add async rendering support #393

1.3.0 (2020-10-30)
==================

- Remove Any from template annotations #343

- Fix type annotation for filters in ``aiohttp_jinja2.setup`` #330

- Drop Python 3.5, support Python 3.9


1.2.0 (2019-10-21)
==================

- Add type hints #285

1.1.1 (2019-04-25)
==================

- Bump minimal supported ``jinja2`` version to 2.10.1 to avoid security vulnerability problem.


1.1.0 (2018-09-05)
==================

- Bump minimal supported ``aiohttp`` version to 3.2

- Use ``request.config_dict`` for accessing ``jinja2`` environment. It
  allows to reuse jinja rendering engine from parent application.

1.0.0 (2018-03-12)
==================

- Allow context_processors to compose from parent apps #195

0.17.0 (2018-03-12)
===================

- Auto-cast ``int`` values in ``url()`` jinja function to ``str`` #191

0.16.0 (2018-02-12)
===================

- Pin to aiohttp 3.0+

- Deprecate non-async handlers support

0.15.0 (2018-01-30)
===================

- Upgrade middleware to new style from aiohttp 2.3+ #182

- Autoescape all templates by default #179


0.13.0 (2016-12-14)
===================

- Avoid subtle errors by copying context processor data #51

0.12.0 (2016-12-02)
===================

- Add autodeploy script #46

0.11.0 (2016-11-24)
===================

- Add jinja2 filters support #41

0.10.0 (2016-10-20)
===================

- Rename package to aiohttp-jinja2 #31

0.9.0 (2016-09-26)
==================

- Fix reason parameter in HTTPInternalServerError when template is not
  found #33

0.8.0 (2016-07-12)
==================

- Add ability to render template without context #28

0.7.0 (2015-12-30)
==================

- Add ability to decorate class based views (available in aiohttp 0.20) #18

- Upgrade aiohttp requirement to version 0.20.0+

0.6.2 (2015-11-22)
==================

- Make app_key parameter from render_string coroutine optional

0.6.0 (2015-10-29)
==================

- Fix a bug in middleware (missed coroutine decorator) #16

- Drop Python 3.3 support (switched to aiohttp version v0.18.0)

- Simplify context processors initialization by adding parameter to `setup()`

0.5.0 (2015-07-09)
==================

- Introduce context processors #14

- Bypass StreamResponse #15

0.4.3 (2015-06-01)
==================

- Fix distribution building: add manifest file

0.4.2 (2015-05-21)
==================

- Make HTTPInternalServerError exceptions more verbose on console
  output

0.4.1 (2015-04-05)
==================

- Documentation update

0.4.0 (2015-04-02)
==================

- Add `render_string` method

0.3.1 (2015-04-01)
==================

- Don't allow non-mapping context

- Fix tiny documentation issues

- Change the library logo

0.3.0 (2015-03-15)
==================

- Documentation release

0.2.1 (2015-02-15)
==================

- Fix `render_template` function

0.2.0 (2015-02-05)
==================

- Migrate to aiohttp 0.14

- Add `status` parameter to template decorator

- Drop optional `response` parameter

0.1.0 (2015-01-08)
==================

- Initial release
