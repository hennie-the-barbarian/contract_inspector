from fastapi import FastAPI, File, UploadFile
from contract_red_flags.tasks import analyze
from pydantic import BaseModel

class Contract(BaseModel):
    contract: str

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

@app.put("/contracts/analyze/file")
async def contract_analyze_file(file: UploadFile):
    task = analyze.analyze_file.delay(file)
    return {"task_id": task.id}