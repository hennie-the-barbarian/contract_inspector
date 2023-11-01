from celery import Celery
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import re
import os

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
        analysis = ContractAnalysis(
            found = True if regex_res else False,
            link = self.link if regex_res else None,
            locations = [[match.span()] for match in regex_res],
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
def analyze_file(contract_file):
    return True

if __name__ == '__main__':
    app.start()