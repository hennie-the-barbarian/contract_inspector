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
import pulumi_docker as docker

from contract_inspector.organization import (
    resource_group,
    cfg
)
from contract_inspector.network import (
    contract_inspector_zone
)
from contract_inspector.docker import (
    registry,
    admin_username,
    admin_password
)
from contract_inspector.messaging import (
    celery_broker,
    celery_backend
)

custom_image = "contract-inspector"
app_path = "../../back-end"

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

api_txt_record = network.RecordSet(
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

api_a_record = network.RecordSet(
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

api_image = docker.Image(
    'contract-inspector-api',
    image_name=registry.login_server.apply(
        lambda login_server: f"{login_server}/{custom_image}-api:v1.0.0"
    ),
    build=docker.DockerBuildArgs(
        context=app_path,
        platform="linux/amd64",
        dockerfile="../../back-end/build/docker/api_dockerfile"
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
        dockerfile="../../back-end/build/docker/worker_dockerfile"
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
                    ),
                    app.EnvironmentVarArgs(
                        name='BLOB_CONNECTION_STRING',
                        ### SAS Info in uri string is strictly needed
                        ### Figure out how to get
                        value=cfg.require_secret("blob-connection-string")
                    ),
                    app.EnvironmentVarArgs(
                        name='BLOB_CONTAINER',
                        ### SAS Info in uri string is strictly needed
                        ### Figure out how to get
                        value='contracts-blob-container'
                    ),
                    app.EnvironmentVarArgs(
                        name='DOCUMENT_INTELLIGENCE_KEY',
                        ### SAS Info in uri string is strictly needed
                        ### Figure out how to get
                        value=cfg.require_secret("document-intelligence-key")
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
                    ),
                    app.EnvironmentVarArgs(
                        name='BLOB_CONNECTION_STRING',
                        ### SAS Info in uri string is strictly needed
                        ### Figure out how to get
                        value=cfg.require_secret("blob-connection-string")
                    ),
                    app.EnvironmentVarArgs(
                        name='BLOB_CONTAINER',
                        ### SAS Info in uri string is strictly needed
                        ### Figure out how to get
                        value='contracts-blob-container'
                    ),
                    app.EnvironmentVarArgs(
                        name='DOCUMENT_INTELLIGENCE_KEY',
                        ### SAS Info in uri string is strictly needed
                        ### Figure out how to get
                        value=cfg.require_secret("document-intelligence-key")
                    )
                ]
            )
        ],
        scale=app.ScaleArgs(
            min_replicas=1
        )
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