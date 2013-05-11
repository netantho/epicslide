# -*- coding: utf-8 -*-

import sys
import os
import pytest
import random
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from epicslide.generator import *
import epicslide.macro


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'samples')
if (not os.path.exists(SAMPLES_DIR)):
    raise IOError('Sample source files not found, cannot run tests')


class TestGenerator(object):
    """
    FACTORIES
    """
    def factory_source(self, tmpdir):
        f = tmpdir.join("tmp.md")
        f.write("Test\n====")
        return str(f)

    def factory_generator(self, tmpdir):
        f = self.factory_source(tmpdir)
        g = Generator(f)
        return g

    def factory_css(self, tmpdir, name="test.css"):
        colors = ('red', 'yellow', 'blue', 'green')
        f = tmpdir.join(name)
        f.write("p {\ntext-color: %s;\n}" % colors[random.randrange(0, 4)])
        return str(f)

    def factory_js(self, tmpdir, name="test.js"):
        colors = ('foo', 'bar', 'baz')
        f = tmpdir.join(name)
        f.write("alert('%s');" % colors[random.randrange(0, 3)])
        return str(f)

    def factory_touch(self, tmpdir, path):
        f = tmpdir.join(path)
        f.write("")
        return str(f)

    """
    TESTS
    """
    def test_init_empty(self):
        with pytest.raises(IOError):
            assert Generator("")

    def test_init_inexistant_file(self):
        with pytest.raises(IOError):
            assert Generator('foo.md')

    def test_init_valid_file(self, tmpdir):
        f = self.factory_source(tmpdir)
        assert Generator(f)

    def test_init_default_arguments(self, tmpdir):
        g = self.factory_generator(tmpdir)
        assert g.source.endswith("tmp.md")
        assert g.copy_theme is False
        assert g.debug is False
        assert g.destination_file == "presentation.html"
        assert g.direct is False
        assert g.embed is False
        assert g.encoding == "utf8"
        assert g.extensions is None
        assert g.logger is None
        assert g.presenter_notes is True
        assert g.relative is False
        assert g.theme == "default"
        assert g.verbose is False

    def test_init_custom_arguments(self, tmpdir):
        f = self.factory_source(tmpdir)
        g = Generator(f,
                      copy_theme=True,
                      debug=True,
                      destination_file="plop.html",
                      direct=True,
                      embed=True,
                      encoding="ascii",
                      # TODO: extensions, logger
                      presenter_notes=False,
                      relative=True,
                      theme='light',
                      verbose=True)
        shutil.rmtree("theme")
        assert g.source == f
        assert g.copy_theme is True
        assert g.debug is True
        assert g.destination_file == "plop.html"
        assert g.direct is True
        assert g.embed is True
        assert g.encoding == "ascii"
        assert g.extensions is None
        assert g.logger is None
        assert g.presenter_notes is False
        assert g.relative is True
        assert g.theme == "light"
        # Because direct is True
        assert g.verbose is False

    def test_add_user_assets_single_notfound(self, tmpdir):
        g = self.factory_generator(tmpdir)
        with pytest.raises(IOError):
            g.add_user_css("notfound.css")
        with pytest.raises(IOError):
            g.add_user_js("notfound.js")

    def test_add_user_assets_single_pass(self, tmpdir):
        g = self.factory_generator(tmpdir)
        css = self.factory_css(tmpdir)
        g.add_user_css(css)
        js = self.factory_js(tmpdir)
        g.add_user_js(js)
        assert g.user_js[0]['path_url'] == "file://%s" % js
        assert g.user_js[0]['contents'] == open(js).read()
        assert g.user_css[0]['path_url'] == "file://%s" % css
        assert g.user_css[0]['contents'] == open(css).read()

    def test_add_user_css_list(self, tmpdir):
        g = self.factory_generator(tmpdir)
        g.user_css = []
        g.user_js = []
        css = []
        js = []
        for i in range(3):
            css.append(self.factory_css(tmpdir, "%d.css" % i))
            js.append(self.factory_js(tmpdir, "%d.js" % i))
        g.add_user_css(css)
        g.add_user_js(js)
        for i in range(3):
            assert g.user_css[i]['path_url'] == "file://%s" % css[i]
            assert g.user_css[i]['contents'] == open(css[i]).read()
            assert g.user_js[i]['path_url'] == "file://%s" % js[i]
            assert g.user_js[i]['contents'] == open(js[i]).read()

    def test_toc(self, tmpdir):
        g = self.factory_generator(tmpdir)
        g.add_toc_entry("test1", 1, 1)
        g.add_toc_entry("test2", 2, 1)
        g.add_toc_entry("test3", 1, 2)
        assert g.toc == [{'sub':
                          [{'sub': [],
                            'level': 2,
                            'number': 1,
                            'title': 'test2'}],
                          'level': 1,
                          'number': 1,
                          'title': 'test1'},
                         {'sub': [],
                          'level': 1,
                          'number': 2,
                          'title': 'test3'}]

    def test_execute_file(self, tmpdir):
        """
        We want execute() to generate a file
        """
        g = self.factory_generator(tmpdir)
        g.destination_file = str(tmpdir.join("presentation.html"))
        g.execute()
        assert os.path.exists(g.destination_file)

    def test_get_template_file(self, tmpdir):
        g = self.factory_generator(tmpdir)
        print g.get_template_file()
        assert g.get_template_file().endswith("/themes/default/base.html")
        g.theme_dir = "/tmp"
        assert g.get_template_file().endswith("/themes/default/base.html")
        g.theme_dir = str(tmpdir)
        f = self.factory_touch(tmpdir, "base.html")
        assert not g.get_template_file().endswith("/themes/default/base.html")

    def test_fetch_contents(self, tmpdir):
        f = self.factory_source(tmpdir)
        g = Generator(f)
        c = g.fetch_contents(f)
        c = c[0]
        assert c['presenter_notes'] is None
        assert c['level'] == 1
        assert c['title'] == "Test"
        assert c['content'] is None
        assert c['header'] == u'<h1>Test</h1>'
        assert c['classes'] == []
        assert c['source']['abs_path'].endswith("tmp.md")
        assert c['source']['rel_path'].endswith("tmp.md")

    def test_find_theme_dir(self, tmpdir):
        g = self.factory_generator(tmpdir)
        g.copy_theme = True
        g.find_theme_dir('default')
        assert g.theme_dir.endswith('themes/default')
        assert os.path.exists(g.theme_dir)
        with pytest.raises(IOError):
            g.find_theme_dir('epictest')

    def test_get_assets(self, tmpdir):
        g = self.factory_generator(tmpdir)
        css = g.get_css()
        js = g.get_js()
        assert 'print' in css
        assert 'screen' in css
        assert css['print']['path_url'].endswith("default/css/print.css")
        assert css['print']['contents']
        assert css['screen']['path_url'].endswith("default/css/screen.css")
        assert css['screen']['contents']
        assert js['path_url'].endswith("default/js/slides.js")
        assert js['contents']

    def test_get_slide_vars(self, tmpdir):
        g = self.factory_generator(tmpdir)
        svars = g.get_slide_vars("<h1>heading</h1>\n<p>foo</p>\n<p>bar</p>\n")
        assert svars['title'] == 'heading'
        assert svars['level'] == 1
        assert svars['header'] == '<h1>heading</h1>'
        assert svars['content'] == '<p>foo</p>\n<p>bar</p>'
        assert svars['source'] == {}
        assert svars['classes'] == []

    def test_get_template_vars(self, tmpdir):
        g = self.factory_generator(tmpdir)
        svars = g.get_template_vars([{'title': "slide1", 'level': 1},
                                     {'title': "slide2", 'level': 1},
                                     {'title': None, 'level': 1}, ])
        assert svars['head_title'] == 'slide1'

    def test_linenos_check(self, tmpdir):
        g = self.factory_generator(tmpdir)
        for value in VALID_LINENOS:
            assert g.linenos_check(value) == value
        assert g.linenos_check("test") == 'inline'

    def test_log(self, tmpdir):
        def custom_logger(message, type):
            assert True
        g = self.factory_generator(tmpdir)
        g.logger = custom_logger
        g.verbose = True
        g.log("hello world!")
        with pytest.raises(ValueError):
            g.logger = "foobar"
            g.log("hello world!")

    def test_parse_config(self, tmpdir):
        g = self.factory_generator(tmpdir)
        conf = g.parse_config(os.path.join(SAMPLES_DIR,
                                           'example4',
                                           'config.cfg'))
        assert conf == {
            'source': ['../example1', '../example2', '../example3'],
            'theme': 'default'
        }

    def test_process_macros(self, tmpdir):
        g = self.factory_generator(tmpdir)
        # Notes
        r = g.process_macros('<p>foo</p>\n<p>.notes: bar</p>\n<p>baz</p>')
        assert r[0].find('<p class="notes">bar</p>') == 11
        assert r[1] == [u'has_notes']
        # FXs
        content = '<p>foo</p>\n<p>.fx: blah blob</p>\n<p>baz</p>'
        r = g.process_macros(content)
        assert r[0] == '<p>foo</p>\n<p>baz</p>'
        assert r[1][0] == 'blah'
        assert r[1][1] == 'blob'

    def test_register_macro(self, tmpdir):
        g = self.factory_generator(tmpdir)

        class SampleMacro(epicslide.macro.Macro):
            pass

        g.register_macro(SampleMacro)
        assert SampleMacro in g.macros

        def plop(foo):
            pass

        with pytest.raises(TypeError):
            g.register_macro(plop)

    def test_render(self, tmpdir):
        g = self.factory_generator(tmpdir)
        assert g.render()

    def test_write(self, tmpdir):
        g = self.factory_generator(tmpdir)
        g.destination_file = str(tmpdir.join("presentation.html"))
        g.write()
        assert os.path.exists(g.destination_file)
        assert unicode(file(g.destination_file).read(), 'utf_8')

    def test_write_pdf(self, tmpdir):
        g = self.factory_generator(tmpdir)
        g.destination_file = str(tmpdir.join("presentation.pdf"))
        g.write_pdf(g.render())
        assert os.path.exists(g.destination_file)

    def test_presenter_notes(self, tmpdir):
        g = self.factory_generator(tmpdir)
        svars = g.get_slide_vars("<h1>heading</h1>\n<p>foo</p>\n"
                                 "<h1>Presenter Notes</h1>\n<p>bar</p>\n")
        assert svars['presenter_notes'] == "<p>bar</p>"

    def test_skip_presenter_notes(self, tmpdir):
        g = self.factory_generator(tmpdir)
        g.presenter_notes = False
        svars = g.get_slide_vars("<h1>heading</h1>\n<p>foo</p>\n"
                                 "<h1>Presenter Notes</h1>\n<p>bar</p>\n")
        assert svars['presenter_notes'] is None

    def test_unicode(self):
        g = Generator(os.path.join(SAMPLES_DIR, 'example3', 'slides.rst'))
        g.execute()
        s = g.render()
        assert s.find('<pre>') != -1
        assert len(re.findall('<pre><span', s)) == 3

    def test_inputencoding(self):
        g = Generator(os.path.join(SAMPLES_DIR, 'example3',
                                   'slides.koi8_r.rst'), encoding='koi8_r')
        content = g.render()
        # check that the string is utf_8
        assert re.findall(u'русский', content,
                          flags=re.UNICODE)
        g.execute()
        file_contents = codecs.open(g.destination_file, encoding='utf_8')\
            .read()
        # check that the file was properly encoded in utf_8
        assert re.findall(u'русский', file_contents,
                          flags=re.UNICODE)
