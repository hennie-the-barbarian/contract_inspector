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