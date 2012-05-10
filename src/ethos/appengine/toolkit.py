import sys, itertools, functools, mako.lookup, haml, webapp2


def _module_for(name):
    '''
    >>> _module_for('this')
    The Zen of Python, by Tim Peters

    Beautiful is better than ugly.
    Explicit is better than implicit.
    Simple is better than complex.
    Complex is better than complicated.
    Flat is better than nested.
    Sparse is better than dense.
    Readability counts.
    Special cases aren't special enough to break the rules.
    Although practicality beats purity.
    Errors should never pass silently.
    Unless explicitly silenced.
    In the face of ambiguity, refuse the temptation to guess.
    There should be one-- and preferably only one --obvious way to do it.
    Although that way may not be obvious at first unless you're Dutch.
    Now is better than never.
    Although never is often better than *right* now.
    If the implementation is hard to explain, it's a bad idea.
    If the implementation is easy to explain, it may be a good idea.
    Namespaces are one honking great idea -- let's do more of those!
    '''
    return __import__(name) and sys.modules[name]


def application(*apps):
    '''
    `apps` is a sequence of names referring to "applications". These are just
    Python modules or packages that contain a `URLS` member listing valid route
    specifications per the docs for `webapp2.Router()`.
    '''
    return webapp2.WSGIApplication(itertools.chain(
        *(_module_for(name).URLS for name in apps)
    ))



class view(dict):
    '''
    A mergeable dictionary that permits access via subscript AND attribute keys,
    i.e. `foo['bar'] == foo.bar`. Instead of raising `KeyError` if missing, an
    empty instance of `view` is returned instead, permitting empty chains, e.g.

    >>> foo = view()
    {}
    >>> if foo.bar.baz.bat: print 'Hello!'

    If none of the keys in the chain have values assigned, no `KeyError` is raised
    and program execution continues.  This kind of behavior is most helpful in
    rendering views, I've found.

    More comprehensive doctests:
    >>> a = view(foo='bar', bar={ 'bat': 'baz' })
    >>> a['foo'] # subscript access
    'bar'
    >>> a.foo # attribute access
    'bar'
    >>> a.bar['bat'] == a.bar.bat == {'bat': 'baz'}
    True
    >>> a.baz # missing key
    {}
    >>> a.baz.bat # chained
    {}
    >>> isinstance(a.baz, view)
    True
    >>> b = dict(bar='baz')
    >>> a + b # merging two views
    {'foo': 'bar', 'bar': 'baz'}
    >>> a # is still intact
    {'foo': 'bar', 'bar': {'bat': 'baz'}}
    >>> b # is still intact
    {'bar': 'baz'}
    >>> b + a # obviously won't work
    Traceback (most recent call last):
        ...
    TypeError: unsupported operand type(s) for +: 'dict' and 'view'
    '''

    @classmethod
    def __missing__(cls, key):
        return cls()


    def __getattr__(self, key):
        return self[key]


    def __setattr__(self, key, value):
        self[key] = value


    def __getitem__(self, key):
        cls = self.__class__

        item = super(view, self).__getitem__(key)

        if isinstance(item, dict) and not isinstance(item, cls):
            return cls(item)

        return item


    def __add__(self, *args):
        new = self.__class__()

        for arg in ((self,) + args): new.update(arg)

        return new



class RequestHandler(webapp2.RequestHandler):
    '''
    Adds optional template rendering to `webapp2.RequestHandler` via Mako
    templates and PyHAML, by default, living in a "templates" directory. To use
    the templates, see `render_template()` or `render_to_response()`.

    Alternately, store values on the `view` (cached) property -- an instance of
    the `view` class -- and use either the `render_template()` or `render_default()`
    decorators.

    >>> class SomeHandler(RequestHandler):
    ...     template_name='path/to/some/template.haml'
    ...
    >>> h = SomeHandler()
    >>> h.view
    {}
    >>> h.view['foo']
    {}
    >>> h.view['foo'] = 'bar'
    >>> h.view['foo']
    'bar'
    >>> h.view['foo'] == h.view.foo
    True
    '''

    template_name=None

    @webapp2.cached_property
    def templates(self):
        return mako.lookup.TemplateLookup([ 'templates' ], preprocessor = haml.preprocessor)


    def template(self, name=None):
        return self.templates.get_template(name or self.template_name)


    @webapp2.cached_property
    def view(self):
        return view()


    def render_template(self, template_name=None, view={}):
        '''
        Returns the result of `mako.Template.render()` for the named template,
        a `cStringIO` object, which will have available `RequestHandler.view` and
        `RequestHandler.url_for()`. The `view` argument will be merged with what's
        already set in `RequestHandler.view`, overriding existing keys, and if no
        `template_name` argument is supplied, the `RequestHandler.template_name`
        is used instead.
        '''
        return self.template(template_name).render(
            view=(self.view + view),
            url_for=self.url_for, # too helpful to get left out...
        )


    def render_to_response(self, template_name=None, view={}):
        '''
        Use `RequestHandler.render_template` to write the rendered `template_name`
        to the `RequestHandler.response`, passing the supplied `view` variables.
        '''
        self.response.out.write(self.render_template(template_name, view))



class render_to_response(object):
    '''
    The `render_to_response()` decorator is designed to be used with a `RequestHandler`
    HTTP method, e.g. `get()`, `post()`. It uses `RequestHandler.render_to_response()`
    under the covers.

    >>> class SomeHandler(RequestHandler):
    ...     template_name='path/to/some/template.haml'
    ...     def get(self):
    ...         self.render_to_response()
    ...     def post(self):
    ...         ## TODO: Process POST request...
    ...         self.render_to_response()
    ...     @render_to_response('path/to/some/other_template.haml')
    ...     def delete(self):
    ...         pass
    ...

    In the example above, the calls to `render_to_response()` in `get()` and `post()`
    use the `template_name` configured on the class, while the `delete()` method
    will use the alternate template. While this isn't much more convenient than
    just calling `self.render_to_response()` with the other template, it does
    keep the processing logic of the method uncluttered.

    Since the decorator is a class instance, you can also use `render_to_response()`
    as a kind of decorator factory for reusable decorators, e.g.

    >>> with_edit_template = render_to_response('path/to/edit.haml')
    >>> class SomeHandler(RequestHandler):
    ...     template_name='path/to/some/common/template.haml'
    ...     def get(self):
    ...         self.render_to_response()
    ...     @with_edit_template
    ...     def post(self):
    ...         pass ## TODO: Process POST request...
    ...

    '''
    template_name = None


    def __init__(self, template_name=None):
        self.template_name = template_name


    def __call__(self, method):
        @functools.wraps(method)
        def wrapper(handler, *args, **kwargs):
            method(handler, *args, **kwargs)

            handler.render_to_response(self.template_name)

        return wrapper


render_default = render_to_response()
render_default.__doc__ = '''
    The `render_default()` decorator is intended for use with a `RequestHandler`
    instance method and just proxies to the `render_template()` decorator with
    no arguments.

    >>> class SomePage(RequestHandler):
    ...   template_name = 'some/template.haml'
    ...   @render_default
    ...   def get(self):
    ...     self.view += { 'foo' : 'bar' }
    ...   def post(self):
    ...     self.redirect_to('home')
    ...   def delete(self):
    ...     self.redirect_to('home')
    ...

    Applying the decorator to `get()` above will cause "some/template.haml" to
    to be rendered to the `Response` with the values assigned to `view`.
    '''



##--- Testing Tools --##
from google.appengine.ext import testbed
import webapp2, unittest2


class GaeTestCase(unittest2.TestCase):
    with_stubs=()

    fixture=None

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        self.init_stubs(*self.with_stubs)


    def init_stubs(self, *initializers):
        [ getattr(self.testbed, i)() for i in initializers ]


    def tearDown(self):
        self.testbed.deactivate()


class with_stubs(object):
    '''
    The `with_stubs()` decorator is expected to be used with test methods of
    `GaeTestCase` and will initialize the named service stubs provided by the
    `GaeTestCase.testbed` instance.

    >>> class SomeTest(GaeTestCase):
    ...   with_stubs=('init_datastore_v3_stub',) # always available
    ...   def test_something(self):
    ...     pass # the datastore can be used in here...
    ...   @with_stubs('init_memcache_stub')
    ...   def test_something(self):
    ...     pass # and the memcache service AND datastore are available here...
    ...

    Use this decorator when you need a stub for a specific test but not for ALL
    tests, set `GaeTestCase.with_stubs` when you ALWAYS need a stub.
    '''

    initializers = ()

    def __init__(self, initializers):
        '''
        The `initializers` argument is a sequence of valid method names of
        the App Engine `Testbed()` instance, e.g. `init_datastore_v3_stub()`.

        Each of these will be invoked BEFORE the decorated method.
        '''
        self.initializers = initializers


    def __call__(self, method):
        @functools.wraps(method)
        def wrapper(test, *args, **kwargs):
            test.init_stubs(*self.initializers)

            return method(test, *args, **kwargs)

        return wrapper



class HandlerTestCase(GaeTestCase):
    request=response=None

    handler=None # override in descendent classes

    application=None # override in descendent classes

    def _url_for(self, name, **kwargs):
        ''' Internal implementation used by `RequestHandlerTestCase.url_for()` '''
        return self.handler.uri_for(name, **kwargs)


    def url_for(self, name, **kwargs):
        ''' The "url_for" method is safe to override in decendent classes. '''
        return self._url_for(name, **kwargs)


    def _request(self, path, method=None, data={}, **kwargs):
        request = webapp2.Request.blank(path, **kwargs)

        request.method = method = method or 'GET'

        request.app = self.application

        if data:
            if method == 'GET':
                request.GET.update(data)

            if method == 'POST':
                request.POST.update(data)

        return request


    def _response(self, *args, **kwargs):
        ''' Returns a new instance of `webapp2.Response()` for use by `HandlerTestCase.route()` '''
        return webapp2.Response(*args, **kwargs)


    def route(self, path=None, method=None, **kwargs):
        self.request = self._request(path, method=method, data=kwargs)

        self.response = self._response()

        self.application.router.dispatch(self.request, self.response)

