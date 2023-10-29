from pydantic_settings import BaseSettings

class AzureSettings(BaseSettings):
    # Defaults to azurite connection string
    blob_connection_string: str = 'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;'
    blob_container: str = 'test-container'

azure_settings = AzureSettings()