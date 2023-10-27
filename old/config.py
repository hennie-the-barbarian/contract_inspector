import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://contract-db.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', 'psZ2eeHIaT0Lli41pabeTj7rAldv3G5se25UCcHimXeJqP581s08az2orwQbce2G3a14dizoWTctACDbugPe4g=='),
    'database_name': os.environ.get('COSMOS_DATABASE', 'ContractRedFlagsDB'),
    'container_name': os.environ.get('COSMOS_CONTAINER', 'Contracts'),
}