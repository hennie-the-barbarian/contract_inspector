from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.tasks.analyze as analyze

def test_analyze_text():
    test_text = "Hello world!"
    assert(analyze.analyze_text(test_text)==True)

def test_analyze_file():
    test_text = "Hello world!"
    assert(analyze.analyze_text(test_text)==True)