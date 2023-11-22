from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import sys
from dataclasses import asdict
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.tasks.analyze as analyze
import contract_red_flags.tasks.contract_analyzers.base_classes as contract_analyzers

def test_analyze_text():
    test_text_short = "This string contains binding arbitration"
    test_result_short = contract_analyzers.ContractAnalysis(
        issues_found=True, 
        warning_issues=[
            contract_analyzers.ContractInfo(
                concern_name='Binding Arbitration', 
                description='Binding arbitration clauses are non-standard in this type of contract. Binding arbitration clauses mean that you are unable to sue the other person in a court over this agreement. The specifics of how the binding arbitration process works will vary depending on the specifics of the clause.', 
                more_info='https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses', 
                concern_level=['WARNING', 'yellow']
            )
        ]
    )

    assert(analyze.analyze_text(test_text_short)==test_result_short)

    test_text_long = "This string contains binding arbitration. And a second binding arbitration."
    test_result_long = contract_analyzers.ContractAnalysis(
        issues_found=True, 
        warning_issues=[
            contract_analyzers.ContractInfo(
                concern_name='Binding Arbitration', 
                description='Binding arbitration clauses are non-standard in this type of contract. Binding arbitration clauses mean that you are unable to sue the other person in a court over this agreement. The specifics of how the binding arbitration process works will vary depending on the specifics of the clause.', 
                more_info='https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses', 
                concern_level=['WARNING', 'yellow']
            )
        ]
    )
    assert(analyze.analyze_text(test_text_long)==test_result_long)

@patch('contract_red_flags.tasks.analyze.azure_settings')
@patch('contract_red_flags.tasks.analyze.analyze_text')
@patch('contract_red_flags.tasks.analyze.AzureKeyCredential')
@patch('contract_red_flags.tasks.analyze.DocumentAnalysisClient')
def test_analyze_file(
    documentAnalysisClientPatch,
    azureKeyCredentialPatch, 
    analyzeTextPatch,
    azureSettingsPatch):
    test_uuid = '1234-1234-1234-ABCD'
    test_key = 'abc123'
    test_muni = 'minneapolis'
    test_contract_type = 'rental-agreement'
    azureSettingsPatch.document_intelligence_key = test_key
    documentAnalysisClientPatch().begin_analyze_document_from_url().result().to_dict.return_value = {
        'documents': [
            {
                "fields": None
            }
        ]
    }
    documentAnalysisClientPatch().begin_analyze_document_from_url().result().content = "Binding arbitration"
    result = analyze.analyze_file(
        test_uuid,
        test_muni,
        test_contract_type
    )
    azureKeyCredentialPatch.assert_called_with(test_key)
    documentAnalysisClientPatch.assert_called_with(
        "https://centralus.api.cognitive.microsoft.com/", 
        azureKeyCredentialPatch())
    documentAnalysisClientPatch().begin_analyze_document_from_url.assert_called_with(
        model_id=test_contract_type,
        document_url=f'https://contractinspectorstorage.blob.core.windows.net/contracts-blob-container/{test_contract_type}/{test_muni}/{test_uuid}'
    )
    expected_output = contract_analyzers.ContractAnalysis(
        issues_found=True, 
        warning_issues = [
            contract_analyzers.ContractInfo(
                concern_name='Binding Arbitration', 
                description='Binding arbitration clauses are non-standard in this type of contract. Binding arbitration clauses mean that you are unable to sue the other person in a court over this agreement. The specifics of how the binding arbitration process works will vary depending on the specifics of the clause.', 
                more_info='https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses', 
                concern_level=['WARNING', 'yellow']
            )
        ]
    )
    assert(result == expected_output)