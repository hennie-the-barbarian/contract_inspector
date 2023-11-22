from unittest.mock import patch
import io
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.tasks.utils as utils

def test_get_muni():
    assert(utils.get_muni() == "Minneapolis, MN")