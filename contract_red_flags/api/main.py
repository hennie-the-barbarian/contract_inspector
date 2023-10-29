from fastapi import FastAPI, File, UploadFile
from contract_red_flags.tasks import analyze
from contract_red_flags.api.settings import azure_settings
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from uuid import uuid4
from celery.result import AsyncResult
from dataclasses import dataclass, asdict

class Contract(BaseModel):
    contract: str

@dataclass
class TaskResult:
    """Class for keeping track of an item in inventory."""
    status: bool
    result: dict

app = FastAPI()

'''
High-level API design
PUT /contracts -> all contracts functionality
PUT /contracts/analyze -> all contract analysis functionality
PUT /contracts/analyze/body -> contract in body of request in text
PUT /contracts/analyze/file -> contract uploaded as a file
'''

@app.put("/contracts/analyze/body")
async def contract_analyze_body(contract: Contract):
    task = analyze.analyze_text.delay(contract.contract)
    return {"task_id": task.id}

@app.get("/contracts/analyze/body/job/{id}")
async def get_contract_analyze_body_job(id):
    result = AsyncResult(id)
    print("AsyncResult")
    print(result)
    result = dict_from_result(result)
    print('DictFromResult')
    print(result)
    return result

@app.put("/contracts/analyze/file")
async def contract_analyze_file(file: UploadFile):
    file_uuid = upload_file(await file.read())
    task = analyze.analyze_file.delay(file_uuid)
    return {"task_id": task.id}

def upload_file(file):
    blob_service_client = BlobServiceClient.from_connection_string(azure_settings.blob_connection_string)
    container_client = blob_service_client.get_container_client(container=azure_settings.blob_container)
    file_uuid = str(uuid4())
    uploaded_blob = container_client.upload_blob(
        name=file_uuid,
        data=file,
        overwrite=True
    )
    return file_uuid

def dict_from_result(result):
    return TaskResult(
        status = result.status,
        result = result.get() if result.status == 'SUCCESS' else None
    )