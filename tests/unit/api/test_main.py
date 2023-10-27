from fastapi.testclient import TestClient
from unittest.mock import patch
import io
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.api.main as main

client = TestClient(main.app)

@patch('contract_red_flags.api.main.analyze')
def test_contract_analyze_body(analyze):
    analyze.analyze_text.delay.return_value.id = 42
    response = client.put(
        "/contracts/analyze/body",
        json={"contract": "Hello world!"})
    assert response.status_code == 200
    assert response.json() == {'task_id': 42}

@patch('contract_red_flags.api.main.analyze')
def test_contract_analyze_file(analyze):
    analyze.analyze_file.delay.return_value.id = 42
    response = client.put("/contracts/analyze/file",
                          files={"file": ("test_file", io.BytesIO(b'Hello world!'))})
    assert response.status_code == 200
    assert response.json() == {'task_id': 42}