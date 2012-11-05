# -*- coding: utf-8 -*-

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/epicslide"))

import main


class TestMain(object):
    @pytest.mark.parametrize(('string', 'options'),
                             [(["slides.md"],
                               {'presenter_notes': True,
                                'verbose': True,
                                'encoding': 'utf8',
                                'linenos': 'inline',
                                'direct': False,
                                'relative': False,
                                'theme': 'default',
                                'extensions': '',
                                'debug': False,
                                'destination_file': 'presentation.html',
                                'embed': False,
                                'copy_theme': False,
                                }),
                              ([''],
                               {'presenter_notes': True,
                                'verbose': True,
                                'encoding': 'utf8',
                                'linenos': 'inline',
                                'direct': False,
                                'relative': False,
                                'theme': 'default',
                                'extensions': '',
                                'debug': False,
                                'destination_file': 'presentation.html',
                                'embed': False,
                                'copy_theme': False,
                                }),
                              (['-r', '-c', '-b', '-d', 'presentation.pdf',
                                '-i', '-l', 'no', '-q', '-t', 'foo',
                                'slides.md'],
                               {'presenter_notes': True,
                                'verbose': False,
                                'encoding': 'utf8',
                                'linenos': 'no',
                                'direct': False,
                                'relative': True,
                                'theme': 'foo',
                                'extensions': '',
                                'debug': True,
                                'destination_file': 'presentation.pdf',
                                'embed': True,
                                'copy_theme': True,
                                }),
                              ],
                             )
    def test_parse_options_pass(self, string, options):
        (roptions, args) = main._parse_options(string)
        print 'roptions', roptions.__dict__
        print 'options', options
        for key in options:
            assert options[key] == roptions.__dict__[key]

    @pytest.mark.parametrize('string',
                             [["-d", "slides.md"],
                              ],
                             )
    def test_parse_options_fail(self, string):
        r = main._parse_options(string)
        assert r == 1

    def test_log(self, capsys):
        main.log('foo', 'notice')
        main.log('bar', 'notice')
        main.log('foo', 'warning')
        main.log('baz', 'warning')
        out, err = capsys.readouterr()
        assert out == 'foo\nbar\n'
        assert err == 'foo\nbaz\n'
