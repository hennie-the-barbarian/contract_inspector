from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import sys
from dataclasses import asdict
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import pprint

import contract_red_flags.tasks.analyze as analyze
import contract_red_flags.tasks.contract_analyzers.base_classes as base_classes

def test_contractAnalysis():
    contract_analysis_a = base_classes.ContractAnalysis(
        issues_found=True, 
        warning_issues= [
            base_classes.ContractInfo(
                concern_name='Binding Arbitration', 
                description='Binding arbitration clauses are non-standard in this type of contract. Binding arbitration clauses mean that you are unable to sue the other person in a court over this agreement. The specifics of how the binding arbitration process works will vary depending on the specifics of the clause.', 
                more_info='https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses', 
                concern_level=['WARNING', 'yellow']
            )
        ]
    )

    contract_analysis_b = base_classes.ContractAnalysis(
        issues_found = True, 
        warning_issues = [
            base_classes.ContractInfo(
                concern_name='Binding Arbitration', 
                description='Binding arbitration clauses are non-standard in this type of contract. Binding arbitration clauses mean that you are unable to sue the other person in a court over this agreement. The specifics of how the binding arbitration process works will vary depending on the specifics of the clause.', 
                more_info='https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses', 
                concern_level=['WARNING', 'yellow']
            )
        ]
    )

    contract_analysis_c = base_classes.ContractAnalysis(
        issues_found=False
    )

    assert(contract_analysis_a==contract_analysis_b)
    assert(contract_analysis_a!=contract_analysis_c)
    assert(
        contract_analysis_a + contract_analysis_c ==
        contract_analysis_b
    )

def test_contract_analyzer():
    factory_output_no_muni = base_classes.ContractAnalyzer.analyzer_factory(
        'rental-agreement'
    )(
        "This text contains binding arbitration",
        {
            'rent':{
                'value': '2000'
            },
            'security_deposit': {
                'value': '3000'
            }
        }
    )

    factory_output_muni = base_classes.ContractAnalyzer.analyzer_factory(
        'rental-agreement',
        [
            "usa",
            "minnesota",
            "hennepin",
            "minneapolis"
        ]
    )(
        "This text contains binding arbitration",
        {
            'rent':{
                'value': '2000'
            },
            'security_deposit': {
                'value': '3000'
            }
        }
    )

def test_get_analyzers():
    analyzers_muni = base_classes.ContractAnalyzer.get_analyzers(
        'rental-agreement',
        [
            "usa",
            "minnesota",
            "hennepin",
            "minneapolis"
        ]
    )

    analyzers_no_muni = base_classes.ContractAnalyzer.get_analyzers(
        'rental-agreement',
        []
    )

    assert(analyzers_muni!=analyzers_no_muni)