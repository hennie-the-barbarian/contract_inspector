import pulumi
from pulumi_azure_native import (
    cognitiveservices
)

from contract_inspector.organization import *
from contract_inspector.network import *
from contract_inspector.messaging import *
from contract_inspector.storage import *
from contract_inspector.ai import *
from contract_inspector.back_end import (
    api_app
)
from contract_inspector.front_end import (
    front_end
)

pulumi.export("api", api_app.configuration.ingress.fqdn)
pulumi.export("front-end", front_end.default_hostname)