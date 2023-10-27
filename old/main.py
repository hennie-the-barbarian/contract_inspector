import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.partition_key import PartitionKey
import config
from extract_text import analyze_read
import sys

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_NAME = config.settings['database_name']
CONTAINER_NAME = config.settings['container_name']

if __name__ == "__main__":
    analyze_read(sys.argv[1])
    