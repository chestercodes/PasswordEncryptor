import boto3
import httplib
from PasswordEncryptor import *

def handler(event, context):
    return handler_impl(event, context, boto3, httplib)