"""
useful context functions, see
http://jinja.pocoo.org/docs/dev/api/#jinja2.contextfunction
"""
import jinja2


@jinja2.contextfunction
def url_for(context, __route_name, **parts):
    """
    filter for generating urls, see
    http://aiohttp.readthedocs.io/en/stable/web.html#reverse-url-constructing-using-named-resources

    Usage: {{ url('the-view-name') }} might become "/path/to/view" or
    {{ url('item-details', id=123, query={'active': 'true'}) }} might become "/items/1?active=true".
    """
    app = context['app']

    query = None
    if 'query_' in parts:
        query = parts.pop('query_')

    url = app.router[__route_name].url_for(**parts)
    if query:
        url = url.with_query(query)
    return url


@jinja2.contextfunction
def static_url(context, static_file_path):
    """
    filter for generating urls for static files. NOTE: you'll need
    to set app['static_root_url'] to be used as  the root for the urls returned.

    Usage: {{ static('styles.css') }} might become "/static/styles.css" or "http://mycdn.example.com/styles.css"
    """
    app = context['app']
    try:
        static_url = app['static_root_url']
    except KeyError:
        raise RuntimeError('app does not define a static root url '
                           '"static_root_url", you need to set the url root '
                           'with `app[\'static_root_url\'] = \'<static root>\'`.')
    return '{}/{}'.format(static_url.rstrip('/'), static_file_path.lstrip('/'))


GLOBAL_HELPERS = dict(
    url=url_for,
    static=static_url,
)
