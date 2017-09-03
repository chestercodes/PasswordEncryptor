__author__ = 'chester.burbidge'

import unittest
from PasswordEncryptor import handler_impl
from moto import mock_s3, mock_kms
import boto3
import json

event={
    'StackId': "SomeId",
    'RequestType': "Get",
    'RequestId': "SomeRequestId",
    'LogicalResourceId': "SomeLogicalResourceId",
    'PhysicalResourceId': "SomePhysicalResourceId",
    'ResourceProperties': {
        'KeyId': 'SomeKeyId',
        'BucketName': 'some-bucket',
        'Encrypt_SomePassword': 'SomePasswordPlain',
        'Encrypt_SomeOtherPassword': 'SomeOtherPasswordPlain'
    },
    'ResponseURL': "SomeResponseURL"
}

class FakeRequest(object):
    def request(self, method, url, body):
        pass
class FakeHttplib(object):
    def HTTPSConnection(self, url):
        return FakeRequest()

@mock_s3
@mock_kms
class PasswordEncryptorTests(unittest.TestCase):
    def test_reads_encrypted_values_from_s3_if_they_exist(self):
        client = boto3.client('s3')
        bucket = 'some-bucket'
        client.create_bucket(Bucket=bucket)
        data = {
            'Password1Encrypted': "SomeEncryptedPassword1",
            'Password2Encrypted': "SomeEncryptedPassword2"
        }
        client.put_object(Bucket=bucket, Key='SomeId_SomeLogicalResourceId', Body=json.dumps(data))

        result = handler_impl(event, {}, boto3, FakeHttplib())

        self.assertTrue("SomePasswordEncrypted" in result['Data'])
        self.assertTrue("SomeOtherPasswordEncrypted" in result['Data'])
        self.assertTrue(result['Data']['Password1Encrypted'] == "SomeEncryptedPassword1")


if __name__ == '__main__':
    unittest.main()
