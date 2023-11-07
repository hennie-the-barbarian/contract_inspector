from celery import Celery
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import re
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from contract_red_flags.api.settings import azure_settings

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
    ## this should kick off the azure OCR using the blob storage URL
    ## send file off to azure OCR
    ## send text from OCR to an analyze text task (chain tasks)
    print("Returning from analyze_file task")
    return True

if __name__ == '__main__':
    app.start()