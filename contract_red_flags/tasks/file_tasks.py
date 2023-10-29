from celery import Celery
import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = Celery("contract_red_flags.tasks.analyze.app",
             broker='amqp://',
             backend='rpc://')

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

