from dataclasses import dataclass
from abc import ABC, abstractmethod
import re

@dataclass
class ContractInfo:
    concern_name: str
    description: str
    more_info: str
    concern_level: str

@dataclass
class ContractAnalysis:
    issues_found: bool
    issues_info: list[ContractInfo]

class ContractAnalyzer(ABC):
    @abstractmethod
    def analyze_contract(self, contract, contract_fields):
        return ContractAnalysis(None, None, None)
    
    ## Whenever this is subclassed, add the subclass to factory_dictionary
    ## Along with its simple name
    factory_dictionary = {}
    def __init_subclass__(cls, simple_name, **kwargs):
        ContractAnalyzer.factory_dictionary[simple_name] = cls
        super().__init_subclass__(**kwargs)

    ## This allows us to get an instance of the subclass from a simple string
    @staticmethod
    def analyzer_factory(contract_type):
        return ContractAnalyzer.factory_dictionary[contract_type]()
    
class RentalAgreementAnalyzer(ContractAnalyzer, simple_name='rental-agreement'):
    def __init__(self) -> None:
        self.label = 'Binding Arbitration'
        self.link = 'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses'
        super().__init__()

    regex = re.compile(r'[bB]inding [aA]rbitration')
    def analyze_contract(self, contract, contract_fields={}):
        issues = {
            "INFORMATION": [],
            "WARNING": [],
            "ILLEGAL": []
        }
        binding_arbitration = binding_arbitration_analysis(contract, is_unusual=True)
        if binding_arbitration:
            issues[binding_arbitration.concern_level[0]].append(binding_arbitration)
        if contract_fields:
            if 'rent' in contract_fields and 'security_deposit' in contract_fields:
                minneapolis_security_deposit = minneapolis_security_deposit_analysis(contract_fields)
                if minneapolis_security_deposit:
                    issues[minneapolis_security_deposit.concern_level[0]].append(minneapolis_security_deposit)
        analysis = ContractAnalysis(
            issues_found = issues != [],
            issues_info = issues
        )
        return analysis

def binding_arbitration_analysis(contract, is_unusual=False):
    label = 'Binding Arbitration'
    link = 'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses'
    level = ['WARNING', 'yellow']
    description_unusual = "Binding arbitration clauses are non-standard in this type of contract."
    description_usual = "Binding arbitration clauses are standard in this type of contract."
    description_all = (
        " Binding arbitration clauses mean that you are unable to sue the other person in a court "
        "over this agreement. The specifics of how the binding arbitration process works will vary "
        "depending on the specifics of the clause."
    )

    regex = re.compile(r'[bB]inding [aA]rbitration')
    regex_res = regex.search(contract)

    if regex_res:
        description = description_unusual if is_unusual else description_usual
        description += description_all
        return ContractInfo(
            concern_name=label,
            concern_level=level,
            more_info=link,
            description=description
        )
    else:
        return None
    
def minneapolis_security_deposit_analysis(contract_fields, non_profit=False):
    label = 'Minneapolis Security Deposit'
    link = 'https://www2.minneapolismn.gov/business-services/licenses-permits-inspections/rental-licenses/renter-protections/security-deposits/'
    description = ""
    concern_level = None
    deposit = int(contract_fields['security_deposit']['value'].strip(' $'))
    rent = int(contract_fields['rent']['value'].strip(' $'))
    deposit_rent_ratio = deposit / rent

    if non_profit==False:
        if 1 > deposit_rent_ratio > .5:
            over_50_perc = deposit - (rent/2)
            description = (
                "Your deposit is more than 1/2 of your monthly rent."
                f" You can request to pay ${int(over_50_perc)} of your deposit over 3 months."
            )
            concern_level = ['INFO', 'blue']
        if deposit_rent_ratio > 1:
            description = (
                "Your potential landlord is requesting an illegal amount of deposit."
                " Please speak with a tenants rights organization immediately."
                " A good place to start: https://homelinemn.org/."
            )
            concern_level = ['ILLEGAL', 'red']
        if deposit_rent_ratio <= .5:
            return None
        return ContractInfo(
            concern_name=label,
            concern_level=concern_level,
            more_info=link,
            description=description
        )
    