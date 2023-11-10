from celery import Celery
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import re
import os
from contract_red_flags.api.settings import azure_settings
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from .contract_analyzers import ContractAnalyzer

broker = os.getenv('CELERY_BROKER',default='amqp://')
backend = os.getenv('CELERY_BACKEND',default='rpc://')

app = Celery("contract_red_flags.tasks.analyze.app",
             broker=broker,
             backend=backend)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

@app.task
def analyze_text(contract_text):
    binding_arbitration_analyzer = ContractAnalyzer.analyzer_factory('rental-agreement')
    binding_arbitration = binding_arbitration_analyzer.analyze_contract(contract_text)
    return asdict(binding_arbitration)

## Need to eventually remove magic strings from here
@app.task
def analyze_file(contract_file_uuid, muni, contract_type):
    endpoint = "https://centralus.api.cognitive.microsoft.com/"
    credential = AzureKeyCredential(azure_settings.document_intelligence_key)
    document_analysis_client = DocumentAnalysisClient(endpoint, credential)
    document_url = f'https://contractinspectorstorage.blob.core.windows.net/contracts-blob-container/{contract_type}/{muni}/{contract_file_uuid}'
    poller = document_analysis_client.begin_analyze_document_from_url(
        model_id=contract_type,
        document_url=document_url
    )
    result = poller.result()
    contract_fields = result.to_dict()['documents'][0]['fields']
    contract_text = result.content
    rental_agreement_analyzer = ContractAnalyzer.analyzer_factory('rental-agreement').analyze_contract
    return asdict(rental_agreement_analyzer(contract_text, contract_fields))

if __name__ == '__main__':
    app.start()