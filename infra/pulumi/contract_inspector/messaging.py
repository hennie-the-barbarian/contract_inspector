import pulumi
from pulumi_azure_native import (
    servicebus
)

from contract_inspector.organization import (
    resource_group
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