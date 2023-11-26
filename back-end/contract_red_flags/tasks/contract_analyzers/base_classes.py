from __future__ import annotations

from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import re

from collections.abc import Callable
from functools import reduce

from . import usa

@dataclass
class ContractInfo:
    concern_name: str
    description: str
    more_info: str
    concern_level: str

    def __json__(self) -> dict:
        return asdict(self)

class ContractAnalysis:
    issues_found: bool
    illegal_issues: list[ContractInfo]
    warning_issues: list[ContractInfo]
    info_issues: list[ContractInfo]
    def __init__(
            self, 
            issues_found, 
            illegal_issues = [],
            warning_issues = [],
            info_issues = []
        ) -> None:
        self.issues_found = issues_found
        self.illegal_issues = illegal_issues
        self.warning_issues = warning_issues
        self.info_issues = info_issues

    def __eq__(self, __value: ContractAnalysis) -> bool:
        return (
            self.issues_found == __value.issues_found and
            self.illegal_issues == __value.illegal_issues and
            self.warning_issues == __value.warning_issues and
            self.info_issues == __value.info_issues
        )
    
    def __add__(self, __value: ContractAnalysis) -> ContractAnalysis:
        return(ContractAnalysis(
            issues_found=self.issues_found or __value.issues_found,
            illegal_issues=self.illegal_issues + __value.illegal_issues,
            warning_issues=self.warning_issues + __value.warning_issues,
            info_issues=self.info_issues+__value.info_issues
        ))
    
    def __repr__(self) -> str:
        return( str( self.__json__() ) )

    def __json__(self) -> dict:
        return {
            'issues_found': self.issues_found,
            'illegal_issues': self.illegal_issues,
            'warning_issues': self.warning_issues,
            'info_issues': self.info_issues
        }

class ContractAnalyzer(ABC):
    @abstractmethod
    def analyze_contract(self, contract, contract_fields):
        return ContractAnalysis(None, None, None)
    
    ## Whenever this is subclassed, add the subclass to factory_dictionary
    ## Along with its simple name
    factory_dictionary = {}
    def __init_subclass__(cls, simple_name, dotted_muni = None, **kwargs):
        ## dotted_muni should be in the form 'nation.state.county.city'
        ## or 'nation.state.cross_county_division'
        ## This is to simplify object lookup
        if dotted_muni:
            ContractAnalyzer.factory_dictionary[
                '{}.{}'.format(
                    simple_name,
                    dotted_muni
                )
            ] = cls
        else:
            ContractAnalyzer.factory_dictionary[simple_name] = cls
        super().__init_subclass__(**kwargs)

    @staticmethod
    def get_analyzers(contract_type, muni: list = []):
        analyzers_list = []
        try:
            analyzers_list.append(ContractAnalyzer.factory_dictionary[contract_type])
        except:
            pass
        current_jurisdiction = contract_type
        for jurisdiction in muni:
            current_jurisdiction += f'.{jurisdiction}'
            try:
                analyzers_list.append(ContractAnalyzer.factory_dictionary[current_jurisdiction])
            except:
                pass
        return analyzers_list

    ## This allows us to get an instance of the subclass from a simple string
    @staticmethod
    def analyzer_factory(contract_type, muni: list = []) -> Callable[str, dict]:
        analyzers_list = [
            analyzer().analyze_contract for analyzer in
            ContractAnalyzer.get_analyzers(contract_type, muni)
        ]
        def generated_func(contract, contract_fields={}):
            mapped_analyzers = [analyzer(contract, contract_fields) for analyzer in analyzers_list]
            reduced_analyzers = reduce(lambda x, y: x+y, mapped_analyzers)
            return reduced_analyzers
        return generated_func

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
        analysis = ContractAnalysis(
            issues_found = issues != [],
            illegal_issues = issues['ILLEGAL'],
            warning_issues = issues['WARNING'],
            info_issues = issues['INFORMATION']
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
