"""
This code sample shows Prebuilt Read operations with the Azure Form Recognizer client library. 
The async versions of the samples require Python 3.6 or later.

To learn more, please visit the documentation - Quickstart: Form Recognizer Python client library SDKs
https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/quickstarts/try-v3-python-sdk
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from pprint import pprint
import json

"""
Remember to remove the key from your code when you're done, and never post it publicly. For production, use
secure methods to store and access your credentials. For more information, see 
https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
"""
endpoint = "https://simple-ocr.cognitiveservices.azure.com/"
key = "2f545449169e4aebb26f06587ae71397"

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])

def analyze_read(doc_path):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    with open(doc_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-read", document=f
        )

        result = poller.result()

        print(dir(result))
        return(result)


if __name__ == "__main__":
    doc_path = 'mn_standard_real_estate.pdf'
    res = analyze_read(doc_path)
    res_json = json.dumps(res.to_dict(), indent=2)
    with open(doc_path + ".json", "w") as f:
        f.write(res_json)

