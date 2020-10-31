"""
useful context functions, see
http://jinja.pocoo.org/docs/dev/api/#jinja2.contextfunction
"""
from typing import Any, Dict, TypedDict, Union, cast

import jinja2
from aiohttp import web
from yarl import URL


class _Context(TypedDict, total=False):
    app: web.Application


@jinja2.contextfunction
def url_for(context: _Context, __route_name: str, **parts: Union[str, int]) -> URL:
    """Filter for generating urls.

    Usage: {{ url('the-view-name') }} might become "/path/to/view" or
    {{ url('item-details', id=123, query={'active': 'true'}) }}
    might become "/items/1?active=true".
    """
    app = context["app"]

    query = None
    if "query_" in parts:
        query = str(parts.pop("query_"))

    parts_clean: Dict[str, str] = {}
    for key in parts:
        val = parts[key]
        if isinstance(val, str):
            # if type is inherited from str expilict cast to str makes sense
            # if type is exactly str the operation is very fast
            val = str(val)
        elif type(val) is int:
            # int inherited classes like bool are forbidden
            val = str(val)
        else:
            raise TypeError(
                "argument value should be str or int, "
                "got {} -> [{}] {!r}".format(key, type(val), val)
            )
        parts_clean[key] = val

    url = app.router[__route_name].url_for(**parts_clean)
    if query:
        url = url.with_query(query)
    return url


@jinja2.contextfunction
def static_url(context: _Context, static_file_path: str) -> str:
    """Filter for generating urls for static files.

    NOTE: you'll need
    to set app['static_root_url'] to be used as the root for the urls returned.

    Usage: {{ static('styles.css') }} might become
    "/static/styles.css" or "http://mycdn.example.com/styles.css"
    """
    app = context["app"]
    try:
        static_url = app["static_root_url"]
    except KeyError:
        raise RuntimeError(
            "app does not define a static root url "
            "'static_root_url', you need to set the url root "
            "with app['static_root_url'] = '<static root>'."
        ) from None
    return "{}/{}".format(static_url.rstrip("/"), static_file_path.lstrip("/"))


GLOBAL_HELPERS = dict(
    url=url_for,
    static=static_url,
)
