import pulumi
from pulumi_azure_native import (
    containerregistry,
    operationalinsights, 
    app, 
    servicebus,
    web,
    network,
    storage,
    cognitiveservices
)
from contract_inspector.organization import (
    resource_group,
    cfg
)
from contract_inspector.network import (
    contract_inspector_zone
)

front_end = web.StaticSite(
    "frontEnd",
    branch="main",
    build_properties=web.StaticSiteBuildPropertiesArgs(
        output_location="dist",
        app_location="/front-end/contract-inspector",
        app_build_command="npm run build"
    ),
    location="Central US",
    name="contractInspectorFrontEnd",
    repository_url="https://github.com/hennie-the-barbarian/contract_inspector",
    repository_token=cfg.require_secret("gh_repo_token"),
    resource_group_name=resource_group.name,
    sku=web.SkuDescriptionArgs(
        name="Free",
        tier="Free",
    )
)

record_set = network.RecordSet(
    resource_name="frontEndRecordSet",
    relative_record_set_name="@",
    record_type="A",
    resource_group_name=resource_group.name,
    ttl=3600,
    zone_name=contract_inspector_zone.name,
    target_resource=network.SubResourceArgs(
        id=front_end.id
    )
)
