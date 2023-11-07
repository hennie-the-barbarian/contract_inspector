from celery import Celery
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import re
import os
from contract_red_flags.api.settings import azure_settings
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

broker = os.getenv('CELERY_BROKER',default='amqp://')
backend = os.getenv('CELERY_BACKEND',default='rpc://')

app = Celery("contract_red_flags.tasks.analyze.app",
             broker=broker,
             backend=backend)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

@dataclass
class ContractAnalysis:
    found: bool
    link: str
    locations: list[list[int]]
    label: str

class ContractAnalyzer(ABC):
    @abstractmethod
    def analyze_contract(self, contract):
        return ContractAnalysis(None, None, None, None)

class BindingArbitrationAnalyzer(ContractAnalyzer):
    def __init__(self) -> None:
        self.label = 'Binding Arbitration'
        self.link = 'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses'
        super().__init__()

    regex = re.compile(r'[bB]inding [aA]rbitration')
    def analyze_contract(self, contract):
        regex_res = self.regex.finditer(contract)
        found_items = [[match.span()] for match in regex_res]
        analysis = ContractAnalysis(
            found = True if found_items else False,
            link = self.link if found_items else None,
            locations = found_items,
            label = self.label
        )
        return analysis

@app.task
def analyze_text(contract_text):
    binding_arbitration_analyzer = BindingArbitrationAnalyzer()
    binding_arbitration = binding_arbitration_analyzer.analyze_contract(contract_text)
    return asdict(binding_arbitration)

## Not implementing file-based analysis at first
@app.task
def analyze_file(contract_file_uuid):
    endpoint = "https://westus.api.cognitive.microsoft.com/"
    credential = AzureKeyCredential(azure_settings.document_intelligence_key)
    document_analysis_client = DocumentAnalysisClient(endpoint, credential)
    document_url = f'https://contractinspectorstorage.blob.core.windows.net/contracts-blob-container/{contract_file_uuid}'
    poller = document_analysis_client.begin_analyze_document_from_url(
        model_id="prebuilt-contract",
        document_url=document_url)
    result = poller.result()
    print("Returning from analyze_file task")
    return analyze_text(result.content)

if __name__ == '__main__':
    app.start()