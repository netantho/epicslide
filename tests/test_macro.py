# -*- coding: utf-8 -*-

import sys
import os
import pytest
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/epicslide"))

import macro


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'samples')
if (not os.path.exists(SAMPLES_DIR)):
    raise IOError('Sample source files not found, cannot run tests')


def logtest(message, type='notice'):
    if type == 'warning':
        raise WarningMessage(message)
    elif type == 'error':
        raise ErrorMessage(message)


class WarningMessage(Exception):
    pass


class ErrorMessage(Exception):
    pass


class TestMacro(object):
    def test_process(self):
        m = macro.Macro()
        r = m.process("<p>foo</p>\n<p>bar</p>")
        assert r[0] == "<p>foo</p>\n<p>bar</p>"
        assert r[1] == []


class TestCodeHighlightingMacro(object):
    def setup_method(self, method):
        self.sample_html = '''<p>Let me give you this snippet:</p>
<pre class="literal-block">
!python
def foo():
    &quot;just a test&quot;
    print bar
</pre>
<p>Then this one:</p>
<pre class="literal-block">
!php
<?php
echo $bar;
?>
</pre>
<p>Then this other one:</p>
<pre class="literal-block">
!xml
<foo>
    <bar glop="yataa">baz</bar>
</foo>
</pre>
<p>End here.</p>'''

    def test_parsing_code_blocks(self):
        m = macro.CodeHighlightingMacro()
        blocks = m.code_blocks_re.findall(self.sample_html)
        assert len(blocks) == 3
        assert blocks[0][2] == 'python'
        assert blocks[0][3].startswith('def foo():')
        assert blocks[1][2] == 'php'
        assert blocks[1][3].startswith('<?php')
        assert blocks[2][2] == 'xml'
        assert blocks[2][3].startswith('<foo>')

    def test_descape(self):
        m = macro.CodeHighlightingMacro()
        assert m.descape('foo') == 'foo'
        assert m.descape('&gt;') == '>'
        assert m.descape('&lt;') == '<'
        assert m.descape('&amp;lt;') == '&lt;'
        assert m.descape('&lt;span&gt;') == '<span>'
        assert m.descape('&lt;spam&amp;eggs&gt;') == '<spam&eggs>'

    def test_process(self):
        m = macro.CodeHighlightingMacro()
        hl = m.process("<pre><code>!php\n$foo;</code></pre>")
        assert hl[0].startswith('<div class="highlight"><pre')
        assert hl[1][0] == u'has_code'
        input = "<p>Nothing to declare</p>"
        assert m.process(input)[0] == input
        assert m.process(input)[1] == []

    def test_process_rst_code_blocks(self):
        m = macro.CodeHighlightingMacro()
        hl = m.process(self.sample_html)
        assert hl[0].startswith('<p>Let me give you this')
        assert hl[0].find('<p>Then this one') > 0
        assert hl[0].find('<p>Then this other one') > 0
        assert hl[0].find('<div class="highlight"><pre') > 0
        assert hl[1][0] == u'has_code'


class TestEmbedImagesMacro(object):
    def test_process(self):
        base_dir = os.path.join(SAMPLES_DIR, 'example1', 'slides.md')
        m = macro.EmbedImagesMacro(logtest, True)
        with pytest.raises(WarningMessage):
            assert m.process('<img src="toto.jpg"/>', '.')
        content, classes = m.process('<img src="monkey.jpg"/>', base_dir)
        assert re.match(r'<img src="data:image/jpeg;base64,(.+?)"/>', content)


class TestFixImagePathsMacro(object):
    def test_process(self):
        base_dir = os.path.join(SAMPLES_DIR, 'example1', 'slides.md')
        m = macro.FixImagePathsMacro(embed=False)
        content, classes = m.process('<img src="monkey.jpg"/>', base_dir)
        assert re.match(r'<img src="file://.*?/monkey.jpg" */>',
                        content)


class TestFxMacro(object):
    def test_process(self):
        m = macro.FxMacro()
        content = '<p>foo</p>\n<p>.fx: blah blob</p>\n<p>baz</p>'
        r = m.process(content)
        assert r[0] == '<p>foo</p>\n<p>baz</p>'
        assert r[1][0] == 'blah'
        assert r[1][1] == 'blob'


class TestNotesMacro(object):
    def test_process(self):
        m = macro.NotesMacro()
        r = m.process('<p>foo</p>\n<p>.notes: bar</p>\n<p>baz</p>')
        assert r[0].find('<p class="notes">bar</p>') == 11
        assert r[1] == [u'has_notes']


class TestQRMacro(object):
    def test_process(self):
        m = macro.QRMacro()
        r = m.process('<p>foo</p>\n<p>.qr: 450'
                      '|http://epicslide.minet.net</p>\n<p>baz</p>')
        assert r[0].find('<p class="qr">'
                         '<img src="http://chart.apis.google.com/'
                         'chart?chs=450x450&cht=qr&chl='
                         'http://epicslide.minet.net'
                         '&chf=bg,s,00000000&choe=UTF-8"'
                         ' alt="QR Code" /></p>') == 11
        assert r[1] == [u'has_qr']
