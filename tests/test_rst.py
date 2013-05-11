# -*- coding: utf-8 -*-

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/epicslide"))

import parser_rst


# class TestRst(object):
#     def test_pygments(self):
#         p = rst.Pygments('')
#         print p.__dict__
#         print p.run()
#         assert False

#     def html_parts(self):
#         assert False
    
#     def html_body(self):
#         assert False
