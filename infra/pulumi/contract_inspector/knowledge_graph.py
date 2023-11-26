import pulumi
from pulumi_azure_native import resources, documentdb

from contract_inspector.organization import (
    resource_group
)

# Create an Azure Cosmos DB account with Gremlin capability
graph_account = documentdb.DatabaseAccount(
    "graph-account",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    database_account_offer_type=documentdb.DatabaseAccountOfferType.STANDARD,
    capabilities=[documentdb.CapabilityArgs(name="EnableGremlin")],
    consistency_policy=documentdb.ConsistencyPolicyArgs(
        default_consistency_level=documentdb.DefaultConsistencyLevel.BOUNDED_STALENESS,
    ),
    locations=[documentdb.LocationArgs(location_name=resource_group.location, failover_priority=0)],
)

# Create a Cosmos DB database within the account
graph_database = documentdb.GremlinResourceGremlinDatabase(
    "graph-database",
    resource_group_name=resource_group.name,
    account_name=graph_account.name,
    database_name="gremlin-database",
    resource=documentdb.GremlinDatabaseResourceArgs(id="gremlin-database")
)

# Create a Graph (i.e., a Gremlin graph) within the Cosmos DB database
graph = documentdb.GremlinResourceGremlinGraph(
    "graph",
    resource_group_name=resource_group.name,
    account_name=graph_account.name,
    database_name=graph_database.resource.id,
    graph_name="laws_munis",
    resource=documentdb.GremlinGraphResourceArgs(
        id="laws_munis",
        partition_key=documentdb.ContainerPartitionKeyArgs(
            kind="Hash",
            paths=["/State"],
        ),
    ),
)
