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

* Create a `virtualenv` for your project:
    * `virtualenv path/to/your/project`
* Enter and activate the `virtualenv`:
    * `cd path/to/your/project && source bin/activate`
* Install it locally:
    * `pip install -e git+https://github.com/al-the-x/ethos-gae-toolkit#egg=ehos-gae-toolkit`
    * This also installs `Mako`[1][1], `PyHAML`[2][2], and `WTForms`[3][3], too.
* Put all your application code somewhere neat:
    * I recommend: `pushd app && cd app && touch app.yaml && popd`
    * Fill out your `app.yaml` file accordingly...
* Put a link to your pip-installed libraries somewhere convenient:
    * `pushd app/ && ln -s ../lib/python2.7/site-packages lib && popd`
    * Assuming you're using the Python 2.7 SDK.
* In every entry-point for your application:
    * `import sys; sys.path = ['lib'] + sys.path`
    * Do yourself a favor and make one `dispatch.py` that serves most if not all URLs...
* Now, when you want to use something in the toolkit:
    ```
    import ethos.appengine.toolkit as toolkit

    class SomeTest(toolkit.GaeTestCase):
    ```

[1]: http://www.makotemplates.org/
[2]: https://github.com/mikeboers/PyHAML/README.md
[3]: http://wtforms.simplecodes.com/docs/dev/crash_course.html
