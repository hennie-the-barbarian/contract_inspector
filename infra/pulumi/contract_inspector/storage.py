import pulumi
from pulumi_azure_native import (
    storage
)
import pulumi_docker as docker

from contract_inspector.organization import (
    resource_group
)

storage_account = storage.StorageAccount(
    "storageAccount",
    resource_group_name=resource_group.name,
    account_name="contractinspectorstorage",
    kind="Storage",
    location="northcentralus",
    sku=storage.SkuArgs(
        name="Standard_LRS",
    ),
)

blob_container = storage.BlobContainer(
    "contractsBlobContainer",
    account_name=storage_account.name,
    container_name="contracts-blob-container",
    resource_group_name=resource_group.name,
)

training_container = storage.BlobContainer(
    "contractModelTrainingBlobContainer",
    account_name=storage_account.name,
    container_name="contracts-model-training-blob-container",
    resource_group_name=resource_group.name,
)

cases_container = storage.BlobContainer(
    "casesBlobContainer",
    account_name=storage_account.name,
    container_name="cases-blob-container",
    resource_group_name=resource_group.name,
)

jurisdictions_container = storage.BlobContainer(
    "jurisdictionsBlobContainer",
    account_name=storage_account.name,
    container_name="jurisdictions-blob-container",
    resource_group_name=resource_group.name,
)