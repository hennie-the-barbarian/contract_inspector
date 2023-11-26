import pulumi
import pulumi_azure_native as azure_native

from contract_inspector.organization import (
    resource_group
)

account = azure_native.maps.Account(
    "mapsAccount",
    account_name="mapsAccount",
    resource_group_name=resource_group.name,
    kind="Gen2",
    location="global",
    sku=azure_native.maps.SkuArgs(
        name="G2"
    )
)