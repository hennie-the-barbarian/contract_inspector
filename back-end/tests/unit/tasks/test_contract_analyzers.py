from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import sys
from dataclasses import asdict
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.tasks.analyze as analyze
import contract_red_flags.tasks.contract_analyzers as contract_analyzers

def test_binding_arbitration_check():
    test_contract = "Binding arbitration"
    expected_result = contract_analyzers.ContractInfo(
        concern_name="Binding Arbitration",
        description=(
            "Binding arbitration clauses are standard in this type of contract."
            " Binding arbitration clauses mean that you are unable to sue the other person in a court "
            "over this agreement. The specifics of how the binding arbitration process works will vary "
            "depending on the specifics of the clause."
        ),
        more_info='https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses',
        concern_level=['WARNING', 'yellow']
    )
    result = contract_analyzers.binding_arbitration_analysis(test_contract)
    assert(result==expected_result)

def test_minneapolis_security_deposit_analysis():
    low_deposit_fields = {
        'security_deposit': {"value": "100"},
        'rent': {"value": "1000"}
    }
    low_deposit_result = contract_analyzers.minneapolis_security_deposit_analysis(low_deposit_fields)
    assert(low_deposit_result==None)

    high_deposit_fields = {
        'security_deposit': {"value": "501"},
        'rent': {"value": "1000"}  
    }
    high_deposit_expected_result = contract_analyzers.ContractInfo(
        concern_name='Minneapolis Security Deposit',
        description=(
            "Your deposit is more than 1/2 of your monthly rent."
            f" You can request to pay $1 of your deposit over 3 months."
        ),
        more_info='https://www2.minneapolismn.gov/business-services/licenses-permits-inspections/rental-licenses/renter-protections/security-deposits/',
        concern_level=['INFO', 'blue']
    )
    high_depost_result = contract_analyzers.minneapolis_security_deposit_analysis(high_deposit_fields)
    assert(high_depost_result==high_deposit_expected_result)

    illegal_deposit_fields = {
        'security_deposit': {"value": "1100"},
        'rent': {"value": "1000"}
    }
    illegal_deposit_expected_result = contract_analyzers.ContractInfo(
        concern_name='Minneapolis Security Deposit',
        description=(
                "Your potential landlord is requesting an illegal amount of deposit."
                " Please speak with a tenants rights organization immediately."
                " A good place to start: https://homelinemn.org/."
            ),
        more_info='https://www2.minneapolismn.gov/business-services/licenses-permits-inspections/rental-licenses/renter-protections/security-deposits/',
        concern_level=['ILLEGAL', 'red']
    )
    illegal_deposit_result = contract_analyzers.minneapolis_security_deposit_analysis(illegal_deposit_fields)
    assert(illegal_deposit_expected_result == illegal_deposit_result)
