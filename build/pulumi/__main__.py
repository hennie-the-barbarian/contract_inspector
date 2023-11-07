# Copyright 2016-2021, Pulumi Corporation.  All rights reserved.

import pulumi
from pulumi_azure_native import (
    containerregistry, 
    operationalinsights, 
    resources,
    app, 
    servicebus,
    web,
    network,
    storage,
    cognitiveservices
)
import pulumi_docker as docker

cfg = pulumi.Config()

app_path = "../.."
image_name = "contract-inspector"
image_tag = "latest"
container_port = 80
cpu = 1
memory = 2
resource_group_name = "contract-inspector"

resource_group = resources.ResourceGroup(resource_group_name)

contract_inspector_zone = network.Zone(
    "contract-inspector",
    location="Global",
    resource_group_name=resource_group.name,
    zone_name="contract-inspector.com"
)

workspace = operationalinsights.Workspace(
    "loganalytics",
    resource_group_name=resource_group.name,
    sku=operationalinsights.WorkspaceSkuArgs(name="PerGB2018"),
    retention_in_days=30
)

workspace_shared_keys = operationalinsights.get_shared_keys(
    resource_group_name=resource_group.name,
    workspace_name=workspace.name
)

namespace = servicebus.Namespace(
    "namespace",
    location="North Central US",
    namespace_name="contract-inspector",
    resource_group_name=resource_group.name,
)

namespace_authorization_rule = servicebus.NamespaceAuthorizationRule(
    "namespaceAuthorizationRule",
    authorization_rule_name="contract-inspector-broker-sas",
    namespace_name=namespace.name,
    resource_group_name=resource_group.name,
    rights=[
        "Manage",
        "Listen",
        "Send"
    ]
)

servicebus_sas_keys = servicebus.list_namespace_keys(
    authorization_rule_name = namespace_authorization_rule.name,
    namespace_name=namespace.name,
    resource_group_name=resource_group.name
)

celery_broker = pulumi.Output.format(
    'azureservicebus://{}:{}@{}', 
    servicebus_sas_keys.key_name, 
    servicebus_sas_keys.primary_key,
    namespace.name
)
celery_backend = 'rpc://'

managed_env = app.ManagedEnvironment(
    "env",
    resource_group_name=resource_group.name,
    app_logs_configuration=app.AppLogsConfigurationArgs(
        destination="log-analytics",
        log_analytics_configuration=app.LogAnalyticsConfigurationArgs(
            customer_id=workspace.customer_id,
            shared_key=workspace_shared_keys.primary_shared_key
        )
    )
)

record_set = network.RecordSet(
    resource_name="apiTXTRecord",
    relative_record_set_name="asuid.api",
    record_type="TXT",
    resource_group_name=resource_group.name,
    ttl=1,
    zone_name=contract_inspector_zone.name,
    txt_records=[network.TxtRecordArgs(
        value=[
            managed_env.custom_domain_configuration.custom_domain_verification_id,
        ],
    )],
)

record_set = network.RecordSet(
    resource_name="apiARecord",
    relative_record_set_name="*",
    record_type="A",
    resource_group_name=resource_group.name,
    ttl=1,
    zone_name=contract_inspector_zone.name,
    a_records=[network.ARecordArgs(
        ipv4_address=managed_env.static_ip,
    )],
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

custom_image = "contract-inspector"
api_image = docker.Image(
    'contract-inspector-api',
    image_name=registry.login_server.apply(
        lambda login_server: f"{login_server}/{custom_image}-api:v1.0.0"
    ),
    build=docker.DockerBuildArgs(
        context=app_path,
        platform="linux/amd64",
        dockerfile="../docker/api_dockerfile"
    ),
    registry=docker.RegistryArgs(
        server=registry.login_server,
        username=admin_username,
        password=admin_password
    )
)

worker_image = docker.Image(
    'contract-inspector-worker',
    image_name=registry.login_server.apply(
        lambda login_server: f"{login_server}/{custom_image}-worker:v1.0.0"
    ),
    build=docker.DockerBuildArgs(
        context=app_path,
        platform="linux/amd64",
        dockerfile="../docker/worker_dockerfile"
    ),
    registry=docker.RegistryArgs(
        server=registry.login_server,
        username=admin_username,
        password=admin_password
    )
)

managed_cert = app.ManagedCertificate(
    "managed_cert",
    environment_name="envd7ba10ff",
    location="North Central US",
    managed_certificate_name="api.contract-inspector.com-envd7ba1-231106000500",
    properties=app.ManagedCertificatePropertiesArgs(
        domain_control_validation="CNAME",
        subject_name="api.contract-inspector.com",
    ),
    resource_group_name="contract-inspector19f4eb7e",
    opts=pulumi.ResourceOptions(protect=True)
)

api_app = app.ContainerApp(
    "api",
    resource_group_name=resource_group.name,
    managed_environment_id=managed_env.id,
    configuration=app.ConfigurationArgs(
        ingress=app.IngressArgs(
            external=True,
            target_port=8000,
            allow_insecure=True,
            cors_policy=app.CorsPolicyArgs(
                allowed_methods=[
                    "*"
                ],
                allowed_origins=[
                    "https://contract-inspector.com",
                    "https://www.contract-inspector.com",
                ]
            ),
            custom_domains=[
                app.CustomDomainArgs(
                    certificate_id=managed_cert.id,
                    name="api.contract-inspector.com",
                )
            ]
        ),
        registries=[
            app.RegistryCredentialsArgs(
                server=registry.login_server,
                username=admin_username,
                password_secret_ref="pwd")
        ],
        secrets=[
            app.SecretArgs(
                name="pwd",
                value=admin_password)
        ],
    ),
    template=app.TemplateArgs(
        containers = [
            app.ContainerArgs(
                name="contract-inspector-api",
                image=api_image.image_name,
                env=[
                    app.EnvironmentVarArgs(
                        name='CELERY_BROKER',
                        ### SAS Info in uri string is strictly needed
                        ### Figure out how to get
                        value=celery_broker
                    )
                ]
            )
        ]
    )
)

worker_app = app.ContainerApp(
    "worker",
    resource_group_name=resource_group.name,
    managed_environment_id=managed_env.id,
    configuration=app.ConfigurationArgs(
        registries=[
            app.RegistryCredentialsArgs(
                server=registry.login_server,
                username=admin_username,
                password_secret_ref="pwd")
        ],
        secrets=[
            app.SecretArgs(
                name="pwd",
                value=admin_password)
        ],
    ),
    template=app.TemplateArgs(
        containers = [
            app.ContainerArgs(
                name="contract-inspector-worker",
                image=worker_image.image_name,
                env=[
                    app.EnvironmentVarArgs(
                        name='WORKER_APP',
                        value='contract_red_flags.tasks.analyze'
                    ),
                    app.EnvironmentVarArgs(
                        name='CELERY_BROKER',
                        value=celery_broker
                    ),
                    app.EnvironmentVarArgs(
                        name='CELERY_RESULT_BACKEND',
                        value=celery_backend
                    )
                ]
            )
        ],
        scale=app.ScaleArgs(
            min_replicas=1
        )
    )
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

record_set = network.RecordSet(
    resource_name="apiRecordSet",
    relative_record_set_name="api",
    record_type="CNAME",
    resource_group_name=resource_group.name,
    ttl=1,
    zone_name=contract_inspector_zone.name,
    cname_record=network.CnameRecordArgs(
        cname=api_app.configuration.ingress.fqdn
    )
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

form_recognizer = cognitiveservices.Account(
    "formRecognizer",
    account_name="contractsFormRecognizer",
    identity=cognitiveservices.IdentityArgs(
        type=cognitiveservices.ResourceIdentityType.SYSTEM_ASSIGNED,
    ),
    kind="FormRecognizer",
    location="West US",
    properties=cognitiveservices.AccountPropertiesArgs(),
    resource_group_name=resource_group.name,
    sku=cognitiveservices.SkuArgs(
        name="F0",
    )
)

pulumi.export("api", api_app.configuration.ingress.fqdn)
pulumi.export("front-end", front_end.default_hostname)