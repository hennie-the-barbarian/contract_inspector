from celery import Celery
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import re
import os
from contract_red_flags.api.settings import azure_settings
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.maps.search import MapsSearchClient
from .contract_analyzers.base_classes import ContractAnalyzer

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
    binding_arbitration_analyzer = ContractAnalyzer.analyzer_factory(
        'rental-agreement',
        []
    )
    binding_arbitration = binding_arbitration_analyzer(contract_text)
    return binding_arbitration

def get_muni_list(contract_fields={}):
    state = contract_fields['state']['value']
    city = contract_fields['city']['value']
    address = contract_fields['street_address']['value']
    address_string = (f'{address}, {city}, {state}')
    ### Search_client needs its own credential
    credential = AzureKeyCredential('s_kMdC-Bl8kTinI2vqB5qnmJP7gbsz3IP8UW3OMxU-E')
    search_client = MapsSearchClient(
        credential=credential,
    )
    fuzzy_search_result = search_client.fuzzy_search(
        query = address_string );
    muni = [
        fuzzy_search_result.results[0].address.country_code_iso3.lower(),
        fuzzy_search_result.results[0].address.country_subdivision_name.lower(),
        fuzzy_search_result.results[0].address.country_secondary_subdivision.lower(),
        fuzzy_search_result.results[0].address.municipality.lower()
    ]
    return muni

## Need to eventually remove magic strings from here
@app.task
def analyze_file(contract_file_uuid, contract_type):
    endpoint = "https://centralus.api.cognitive.microsoft.com/"
    credential = AzureKeyCredential(azure_settings.document_intelligence_key)
    document_analysis_client = DocumentAnalysisClient(endpoint, credential)
    document_url = f'https://contractinspectorstorage.blob.core.windows.net/contracts-blob-container/{contract_type}/{contract_file_uuid}'
    poller = document_analysis_client.begin_analyze_document_from_url(
        model_id=contract_type,
        document_url=document_url
    )
    result = poller.result()
    contract_fields = result.to_dict()['documents'][0]['fields']
    contract_text = result.content
    muni=get_muni_list(contract_fields)
    rental_agreement_analyzer = ContractAnalyzer.analyzer_factory(
        contract_type, 
        muni
    )
    analyzer_result = rental_agreement_analyzer(contract_text, contract_fields)
    print("Return value from analyze.py")
    print(analyzer_result)
    return analyzer_result

if __name__ == '__main__':
    app.start()