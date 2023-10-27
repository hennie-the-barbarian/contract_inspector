import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.partition_key import PartitionKey
import config

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_NAME = config.settings['database_name']
CONTAINER_NAME = config.settings['container_name']

if __name__ == "__main__":
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="ContractRedFlagsCLI", user_agent_overwrite=True)

    database = client.create_database_if_not_exists(id=DATABASE_NAME)
    print("Database\t", database.id)

    container = database.create_container_if_not_exists(id=CONTAINER_NAME, partition_key=PartitionKey(path='/partitionKey'))
    print('Container\t', container.id)
