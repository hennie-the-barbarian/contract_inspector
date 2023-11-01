# Copyright 2016-2021, Pulumi Corporation.  All rights reserved.

import pulumi
from pulumi_azure_native import containerregistry
from pulumi_azure_native import operationalinsights
from pulumi_azure_native import resources
from pulumi_azure_native import app
from pulumi_azure_native import servicebus
import pulumi_docker as docker

app_path = "../.."
image_name = "contract-inspector"
image_tag = "latest"
container_port = 80
cpu = 1
memory = 2
resource_group_name = "contract-inspector"

resource_group = resources.ResourceGroup(resource_group_name)

workspace = operationalinsights.Workspace(
    "loganalytics",
    resource_group_name=resource_group.name,
    sku=operationalinsights.WorkspaceSkuArgs(name="PerGB2018"),
    retention_in_days=30
)

workspace_shared_keys = pulumi.Output.all(resource_group.name, workspace.name) \
    .apply(lambda args: operationalinsights.get_shared_keys(
        resource_group_name=args[0],
        workspace_name=args[1]
    ))

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

managed_env = app.ManagedEnvironment("env",
    resource_group_name=resource_group.name,
    app_logs_configuration=app.AppLogsConfigurationArgs(
        destination="log-analytics",
        log_analytics_configuration=app.LogAnalyticsConfigurationArgs(
            customer_id=workspace.customer_id,
            shared_key=workspace_shared_keys.apply(lambda r: r.primary_shared_key)
        )
    )
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

api_app = app.ContainerApp(
    "api",
    resource_group_name=resource_group.name,
    managed_environment_id=managed_env.id,
    configuration=app.ConfigurationArgs(
        ingress=app.IngressArgs(
            external=True,
            target_port=8000
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

'''worker_job = app.Job(
    "job",
    configuration=azure_native.app.JobConfigurationResponseArgs(
        event_trigger_config={
            "parallelism": 4,
            "replicaCompletionCount": 1,
            "scale": {
                "maxExecutions": 5,
                "minExecutions": 1,
                "pollingInterval": 40,
                "rules": [app.JobScaleRuleArgs(
                    metadata={
                        "topicName": "my-topic",
                    },
                    name="contract-inspector-celery-queue-rule",
                    type="azure-servicebus",
                )],
            },
        },
        replica_retry_limit=10,
        replica_timeout=10,
        trigger_type="Event",
    ),
    managed_environment_id=managed_env.id,
    job_name="contract-inspector-worker-job",
    location="North Central US",
    resource_group_name=resource_group.name,
    template=app.JobTemplateResponseArgs(
        containers=[{
            "image": "repo/testcontainerAppsJob0:v1",
            "name": "testcontainerAppsJob0",
            "probes": [{
                "httpGet": {
                    "httpHeaders": [
                        app.ContainerAppProbeHttpHeadersArgs(
                            name="Custom-Header",
                            value="Awesome",
                        )
                    ],
                    "path": "/health",
                    "port": 8080,
                },
                "initialDelaySeconds": 5,
                "periodSeconds": 3,
                "type": "Liveness",
            }],
        }]
    )
)
'''

pulumi.export("api", api_app.configuration.apply(lambda c: c.ingress).apply(lambda i: i.fqdn))