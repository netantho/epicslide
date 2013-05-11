# -*- coding: utf-8 -*-

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from epicslide import parser


class TestParserTest():
    def test_init(self):
        assert parser.Parser('.md').format == 'markdown'
        assert parser.Parser('.markdown').format == 'markdown'
        assert parser.Parser('.rst').format == 'restructuredtext'
        assert parser.Parser('.textile').format == 'textile'
        with pytest.raises(NotImplementedError):
            parser.Parser('.txt')

    def test_init_md_extensions(self):
        p = parser.Parser('.md', md_extensions='a,b,c')
        assert p.md_extensions == ['a', 'b', 'c']

    @pytest.mark.parametrize(('format', 'input', 'output'),
                             [('.md', 'Hello World!\n============',
                               '<h1>Hello World!</h1>'),
                              ('.md', '`p`\n**Hello** _Gentlemen_\n\n'
                               '- Mega Man 2\n- Mega Man 3',
                               '<p><code>p</code>\n'
                               '<strong>Hello</strong> '
                               '<em>Gentlemen</em></p>\n'
                               '<ul>\n'
                               '<li>Mega Man 2</li>\n'
                               '<li>Mega Man 3</li>\n'
                               '</ul>'),
                              ('.rst', 'Header\n======\n'
                               'Subheader\n---------\n'
                               '.. image:: image.jpg\n'
                               '.. _Wikipedia: http://www.wikipedia.org/',
                               '<h1>Header</h1>\n'
                               '<h2>Subheader</h2>\n'
                               '<img alt="image.jpg" src="image.jpg" />'),
                              ('.textile', '+a+\n'
                               '%{color:blue}foo%\n'
                               '"Link to Wikipedia":http://www.wikipedia.org',
                               '\t<p><ins>a</ins><br />'
                               '<span style="color:blue;">foo</span><br />'
                               '<a href="http://www.wikipedia.org">'
                               'Link to Wikipedia</a></p>')
                              ],
                             )
    def test_parse(self, format, input, output):
        p = parser.Parser(format)
        r = p.parse(input)
        assert r == output

    def test_parse_unicode_nom(self):
        p = parser.Parser('.md')
        r = p.parse(u'\ufeffplop')  # unicode BOM
        assert r == '<p>plop</p>'

    def test_parse_unknown_format(self):
        p = parser.Parser('.md')
        p.format = '.plop'
        with pytest.raises(NotImplementedError):
            p.parse('foo bar')
