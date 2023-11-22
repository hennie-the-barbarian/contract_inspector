import re
from ....base_classes import (
    ContractAnalyzer, 
    ContractAnalysis, 
    ContractInfo, 
    binding_arbitration_analysis
)

class RentalAgreementAnalyzer(ContractAnalyzer, simple_name='rental-agreement'):
    def __init__(self) -> None:
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
            concern_level = ['INFORMATION', 'blue']
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
    