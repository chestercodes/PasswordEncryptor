import base64
import uuid
import json
import logging

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# This function takes in the values from the stack which are sensitive and encrypts them with the key specified.abs
# It then returns them to be used in the CustomResource in the cloudformation stack

def send_response(httplib, request, response, status=None, reason=None):
    """ Send our response to the pre-signed URL supplied by CloudFormation
    If no ResponseURL is found in the request, there is no place to send a
    response. This may be the case if the supplied event was for testing.
    """

    if status is not None:
        response['Status'] = status

    if reason is not None:
        response['Reason'] = reason

    if 'ResponseURL' in request and request['ResponseURL']:
        url = urlparse(request['ResponseURL'])
        body = json.dumps(response)
        https = httplib.HTTPSConnection(url.hostname)
        https.request('PUT', url.path+'?'+url.query, body)

    return response

def failed_response(httplib, failed_reason, event_arg, response_arg):
    return send_response(httplib,
        event_arg, response_arg, status='FAILED',
        reason=failed_reason
    )

def handler_impl(event, context, boto, httplib):
    logger.info("ResponseUrl is " + event['ResponseURL'])
    response = {
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Status': 'SUCCESS'
    }

    # PhysicalResourceId is meaningless here, but CloudFormation requires it
    if 'PhysicalResourceId' in event:
        response['PhysicalResourceId'] = event['PhysicalResourceId']
    else:
        response['PhysicalResourceId'] = str(uuid.uuid4())

    # There is nothing to do for a delete request
    if event['RequestType'] == 'Delete':
        return send_response(httplib, event, response)

    kms_client = boto.client('kms')

    # Encrypt the values using AWS KMS and return the response
    try:
        res_props = event['ResourceProperties']
        if 'KeyId' not in res_props or not res_props['KeyId']:
            logger.info("KeyId validation failed")
            return failed_response(httplib, 'KeyId not present', event, response)

        key_id = res_props['KeyId']
        data = dict()
        encrypt_placeholder = "Encrypt_"
        to_encrypt_keys =  filter(lambda key: key.startswith(encrypt_placeholder), res_props.keys())
        for to_encrypt_key in to_encrypt_keys:
            encrypted = kms_client.encrypt(KeyId=key_id, Plaintext=res_props[to_encrypt_key])
            val = base64.b64encode(encrypted['CiphertextBlob'])
            name = to_encrypt_key[len(encrypt_placeholder):] + "Encrypted"
            data[name] = val.decode("utf-8")

        if 'BucketName' in res_props:
            logger.info("BucketName specified, try to write many random passwords")


        response['Data'] = data
        response['Reason'] = 'The value was successfully encrypted'

    except Exception as E:
        logger.error("Error - " + str(E))
        response['Status'] = 'FAILED'
        response['Reason'] = 'Encryption Failed - See CloudWatch logs for the Lamba function backing the custom resource for details'

    return send_response(httplib, event, response)