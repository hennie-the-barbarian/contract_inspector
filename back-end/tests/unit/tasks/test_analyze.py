from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import sys
from dataclasses import asdict
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.tasks.analyze as analyze

def test_analyze_text():
    test_text_short = "This string contains binding arbitration"
    test_result_short = asdict(    
        analyze.ContractAnalysis(
            True,
            'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses',
            [(21, 40)],
            'Binding Arbitration'
        )
    )
    assert(analyze.analyze_text(test_text_short)==test_result_short)

    test_text_long = "This string contains binding arbitration. And a second binding arbitration."
    # Ordering matters due to how re.matchiter works underlyingly
    test_result_long = asdict(
        analyze.ContractAnalysis(
            True,
            'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses',
            [(21, 40), (55, 74)],
            'Binding Arbitration'
        )
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
    azureSettingsPatch.document_intelligence_key = test_key
    result = analyze.analyze_file(test_uuid)
    azureKeyCredentialPatch.assert_called_with(test_key)
    documentAnalysisClientPatch.assert_called_with(
        "https://westus.api.cognitive.microsoft.com/", 
        azureKeyCredentialPatch())
    documentAnalysisClientPatch().begin_analyze_document_from_url.assert_called_with(
        model_id="prebuilt-contract",
        document_url=f'https://contractinspectorstorage.blob.core.windows.net/contracts-blob-container/{test_uuid}'
    )
    assert(result == analyzeTextPatch(
        documentAnalysisClientPatch().begin_analyze_document_from_url().result().content
    ))