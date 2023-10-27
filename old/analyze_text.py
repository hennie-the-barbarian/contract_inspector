import json
from pprint import pprint

def analyze_contract(contract_json):
    print(contract_json.keys())
    for para in contract_json['paragraphs'][-10:-1]:
        print(para['content'])
    ## print(contract_json['content'])

if __name__ == "__main__":
    doc_path = 'mn_standard_real_estate.pdf.json'
    with open(doc_path, "rb") as f:
        pdf_json = json.loads(f.read())
        analyze_contract(pdf_json)