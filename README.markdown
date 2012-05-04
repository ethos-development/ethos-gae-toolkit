ethos Toolkit for Google App Engine
===================================

I love me some Google App Engine. And while I do love me some Django, too, sometimes
the full Django stack is just too much. Anymore, I prefer writing small, ReSTful
applications using just `webapp` and `webapp2`, `Mako+HAML` templates, and `WTForms`.
This little toolkit describes that stack nicely and provides some nice integrations
for them as well as some decent unit testing tools for `RequestHandler` classes.

How to use this toolkit...
--------------------------

I recommend using `virtualenv` to manage your environment and track dependencies.
Since Google App Engine is expecting (read: REQUIRES) just a big, messy bucket of
code -- libraries, dependencies and all -- here's how I keep things pretty:

Create a `virtualenv` for your project:

```
$> virtualenv path/to/your/project
```

Enter and activate the `virtualenv`:

```
$> cd path/to/your/project && source bin/activate
```

Install it locally<sup>[1](#fn1)</sup>

```
$> pip install -e git+https://github.com/al-the-x/ethos-gae-toolkit#egg=ehos-gae-toolkit
```

Put all your application code somewhere neat, I recommend:

```
$> pushd app && cd app && touch app.yaml && popd
```

Put a link to your pip-installed libraries somewhere convenient<sup>[2](#fn2)</sup>:

```
$> pushd app/ && ln -s ../lib/python2.7/site-packages lib && popd
```

In every entry-point for your application, make the `lib/` path available for import<sup>[3](#fn3)</sup>:

```
import sys

sys.path = ['lib'] + sys.path
```

Now, when you want to use something in the toolkit:

```
import ethos.appengine.toolkit as toolkit

class SomeTest(toolkit.GaeTestCase):
```

### Footnotes:

<dl>
<dt> <a name="fn1">1</a> </dt>
<dd> This also installs [`Mako`][], [`PyHAML`][], and [`WTForms`][], too. </dd>
<dt> <a name="fn2">2</a> </dt>
<dd> Assuming you're using the Python 2.7 SDK. Change the path for the 2.5 SDK. </dd>
<dt> <a name="fn3">3</a> </dt>
<dd> Do yourself a favor and make one `dispatch.py` that serves most if not all of your URLs to make this easy. </dd>
</dl>

[Mako]: http://www.makotemplates.org/
[PyHAML]: https://github.com/mikeboers/PyHAML/README.md
[WTForms]: http://wtforms.simplecodes.com/docs/dev/crash_course.html
