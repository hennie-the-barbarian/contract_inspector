from fastapi.testclient import TestClient
from unittest.mock import patch
import io
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.tasks.file_tasks as file_tasks

def test_upload_file():
    assert file_tasks.upload_file('test_file.pdf') == True