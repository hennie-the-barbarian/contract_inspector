import pulumi
from pulumi_azure_native import (
    containerregistry,
    resources,
    app, 
    servicebus,
    web,
    network,
    storage,
    cognitiveservices
)

resource_group_name = "contract-inspector"

resource_group = resources.ResourceGroup(resource_group_name)

cfg = pulumi.Config()