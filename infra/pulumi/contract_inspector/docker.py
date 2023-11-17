import pulumi
from pulumi_azure_native import (
    containerregistry,
    app, 
    servicebus,
    web,
    network,
    storage,
    cognitiveservices
)
import pulumi_docker as docker

from contract_inspector.organization import (
    resource_group
)

registry = containerregistry.Registry(
    "registry",
    resource_group_name=resource_group.name,
    sku=containerregistry.SkuArgs(name="Basic"),
    admin_user_enabled=True
)

credentials = pulumi.Output.all(resource_group.name, registry.name).apply(
    lambda args: containerregistry.list_registry_credentials(resource_group_name=args[0],
                                                             registry_name=args[1]))
admin_username = credentials.username
admin_password = credentials.passwords[0]["value"]