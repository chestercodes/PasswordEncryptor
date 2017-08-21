from PasswordEncryptor import *

#{
#  "RequestType": "Create",
#  "ServiceToken": "arn:aws:lambda:...:function:route53Dependency",
#  "ResponseURL": "https://cloudformation-custom-resource...",
#  "StackId": "arn:aws:cloudformation:eu-west-1:...",
#  "RequestId": "afd8d7c5-9376-4013-8b3b-307517b8719e",
#  "LogicalResourceId": "Route53",
#  "ResourceType": "Custom::Route53Dependency",
#  "ResourceProperties": {
#    "ServiceToken": "arn:aws:lambda:...:function:route53Dependency",
#    "DomainName": "example.com"
#  }
#}

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

context={

}
class FakeRequest(object):
    def request(self, method, url, body):
        pass
class FakeHttplib(object):
    def HTTPSConnection(self, url):
        return FakeRequest()

class FakeKms(object):
    def encrypt(self, KeyId, Plaintext):
        return {"CiphertextBlob": "some_value".encode()}

class FakeS3Object(object):
    def loads(self):
        return {"Object": ""}

class FakeS3(object):
    def encrypt(self, KeyId, Plaintext):
        return {"Object": FakeS3Object()}
    def get_object(self, Bucket, Key):
        return ""
    def list_objects(self, Bucket, Prefix):
        return {}
class FakeBoto(object):
    def client(self, client_name):
        if client_name == "s3":
            return FakeS3()
        return FakeKms()

handler_impl(event, context, FakeBoto(), FakeHttplib())