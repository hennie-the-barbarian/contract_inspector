from fastapi import FastAPI, File, UploadFile, Path, Query, HTTPException
from contract_red_flags.tasks import analyze
from contract_red_flags.api.settings import azure_settings
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from uuid import uuid4
from celery.result import AsyncResult
from dataclasses import dataclass, asdict
from fastapi.middleware.cors import CORSMiddleware

class Contract(BaseModel):
    contract: str

@dataclass
class TaskResult:
    """Class for keeping track of an item in inventory."""
    status: bool
    result: dict

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.put("/contracts/analyze/body")
async def contract_analyze_body(contract: Contract):
    task = analyze.analyze_text.delay(contract.contract)
    return {"task_id": task.id}

@app.get("/contracts/analyze/body/job/{id}")
async def get_contract_analyze_body_job(id):
    result = AsyncResult(id)
    result = dict_from_result(result)
    return result

@app.put("/contracts/analyze/file/{contract_type}")
async def contract_analyze_file(file: UploadFile, contract_type):
    file_uuid = upload_file(await file.read(), contract_type)
    task = analyze.analyze_file.delay(file_uuid, contract_type)
    return {"task_id": task.id}

@app.get("/contracts/analyze/file/job/{id}")
async def get_contract_analyze_file_job(id):
    result = AsyncResult(id)
    result = dict_from_result(result)
    print("Result from api")
    print(result)
    return result

def upload_file(file, contract_type):
    blob_service_client = BlobServiceClient.from_connection_string(azure_settings.blob_connection_string)
    container_client = blob_service_client.get_container_client(container=azure_settings.blob_container)
    file_uuid = str(uuid4())
    uploaded_blob = container_client.upload_blob(
        name=f'{contract_type}/{file_uuid}',
        data=file,
        overwrite=True
    )
    return file_uuid

def dict_from_result(result):
    return TaskResult(
        status = result.status,
        result = result.get() if result.status == 'SUCCESS' else None
    )