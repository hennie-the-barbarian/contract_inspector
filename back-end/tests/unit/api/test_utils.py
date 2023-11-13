from unittest.mock import patch
import io
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.api.utils as utils

def test_is_txt():
    txt_file = open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'files/test.txt')), 'r')
    assert(utils.is_txt(txt_file) == True)

    pdf_file = open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'files/test.pdf')), 'r')