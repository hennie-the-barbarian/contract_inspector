from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import sys
from dataclasses import asdict
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.tasks.analyze as analyze

def test_analyze_text():
    test_text_short = "This string contains binding arbitration"
    test_result_short = [
        asdict(    
            analyze.ContractAnalysis(
                True,
                'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses',
                (21, 40),
                'Binding Arbitration'
            )
        )
    ]
    assert(analyze.analyze_text(test_text_short)==test_result_short)

    test_text_long = "This string contains binding arbitration. And a second binding arbitration."
    # Ordering matters due to how re.matchiter works underlyingly
    test_result_long = [
        asdict(
            analyze.ContractAnalysis(
                True,
                'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses',
                (21, 40),
                'Binding Arbitration'
            )
        ),
        asdict(
            analyze.ContractAnalysis(
                True,
                'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses',
                (55, 74),
                'Binding Arbitration'
            )
        )
    ]
    assert(analyze.analyze_text(test_text_long)==test_result_long)

def test_analyze_file():
    test_text = "Hello world!"
    assert(analyze.analyze_file(test_text)==True)