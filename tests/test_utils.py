# -*- coding: utf-8 -*-

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from epicslide import utils


def test_get_path_url_relative():
    u = utils.get_path_url('/plop', relative=True)
    assert u == '/plop'
