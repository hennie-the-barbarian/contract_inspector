from fastapi.testclient import TestClient
from unittest.mock import patch
import io
import os
import sys
from uuid import UUID
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.api.main as main

client = TestClient(main.app)

@patch('contract_red_flags.api.main.analyze')
def test_contract_analyze_body(analyze_mock):
    analyze_mock.analyze_text.delay.return_value.id = 42
    response = client.put(
        "/contracts/analyze/body",
        json={"contract": "Hello world!"})
    assert response.status_code == 200
    assert response.json() == {'task_id': 42}

@patch('contract_red_flags.api.main.upload_file')
@patch('contract_red_flags.api.main.analyze')
def test_contract_analyze_file(analyze_mock, upload_file_mock):
    test_string = b'Hello world!'
    test_bytes = io.BytesIO(test_string)
    analyze_mock.analyze_file.delay.return_value.id = 42
    response = client.put("/contracts/analyze/file",
                          files={"file": ("test_file", test_bytes)})
    assert response.status_code == 200
    assert response.json() == {'task_id': 42}
    upload_file_mock.assert_called_with(test_string)

@patch('contract_red_flags.api.main.BlobServiceClient')
@patch('contract_red_flags.api.main.uuid4')
def test_upload_file(uuid4_mock, blob_service_client_mock):
    test_bytes = io.BytesIO(b'Hello world!')
    test_uuid = '12345678-1234-5678-1234-567812345678'
    uuid4_mock.return_value = UUID(test_uuid)
    file_uuid = main.upload_file(test_bytes)
    assert file_uuid == test_uuid
    blob_service_client_mock.from_connection_string().get_container_client().upload_blob.assert_called_with(
        name=file_uuid,
        data=test_bytes,
        overwrite=True
    )

@patch('contract_red_flags.api.main.AsyncResult')
def test_get_contract_analyze_body_job(async_result_mock):
    expected_output = {
        'status': 'SUCCESS', 
        'result': {
            'found': True,
            'link': 'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses', 
            'locations': [[21, 40]],
            'label': 'Binding Arbitration'
        }
    }
    async_result_mock.return_value.status = "SUCCESS"
    async_result_mock.return_value.get.return_value = {
        'found': True, 
        'link': 'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses', 
        'locations': [(21, 40)],
        'label': 'Binding Arbitration'
    } 
    response = client.get("/contracts/analyze/body/job/42")
    print(response.json())
    assert response.json() == expected_output

@patch('contract_red_flags.api.main.AsyncResult')
def test_get_contract_analyze_file_job(async_result_mock):
    expected_output = {
        'status': 'SUCCESS', 
        'result': {
            'found': True,
            'link': 'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses', 
            'locations': [[21, 40]],
            'label': 'Binding Arbitration'
        }
    }
    async_result_mock.return_value.status = "SUCCESS"
    async_result_mock.return_value.get.return_value = {
        'found': True, 
        'link': 'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses', 
        'locations': [(21, 40)],
        'label': 'Binding Arbitration'
    } 
    response = client.get("/contracts/analyze/file/job/42")
    print(response.json())
    assert response.json() == expected_output

