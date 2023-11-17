import pulumi
from pulumi_azure_native import (
    network
)
from .organization import (
    resource_group
)

contract_inspector_zone = network.Zone(
    "contract-inspector",
    location="Global",
    resource_group_name=resource_group.name,
    zone_name="contract-inspector.com"
)