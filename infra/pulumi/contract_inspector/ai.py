from pulumi_azure_native import (
    cognitiveservices,
    search
)
from contract_inspector.organization import (
    resource_group
)

form_recognizer = cognitiveservices.Account(
    "formRecognizer",
    account_name="contractsFormRecognizer",
    identity=cognitiveservices.IdentityArgs(
        type=cognitiveservices.ResourceIdentityType.SYSTEM_ASSIGNED,
    ),
    kind="FormRecognizer",
    location="Central US",
    properties=cognitiveservices.AccountPropertiesArgs(),
    resource_group_name=resource_group.name,
    sku=cognitiveservices.SkuArgs(
        name="S0",
    )
)

service = search.Service(
    "casesSearch",
    location="northcentralus",
    resource_group_name=resource_group.name,
    search_service_name="cases-search",
    sku=search.SkuArgs(
        name=search.SkuName.FREE,
    )
)

form_recognizer = cognitiveservices.Account(
    "contractInspectorCognitiveServices",
    account_name="contractInspectorCognitiveServices",
    identity=cognitiveservices.IdentityArgs(
        type=cognitiveservices.ResourceIdentityType.SYSTEM_ASSIGNED,
    ),
    kind="CognitiveServices",
    location="North Central US",
    properties=cognitiveservices.AccountPropertiesArgs(),
    resource_group_name=resource_group.name,
    sku=cognitiveservices.SkuArgs(
        name="S0",
    )
)