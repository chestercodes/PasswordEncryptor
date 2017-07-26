from PasswordEncryptor import *

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

class FakeHttplib(object):
    def client(self, client_name, Plaintext):
        return {'CiphertextBlob': "1234"}

class FakeKms(object):
    def encrypt(self, KeyId, Plaintext):
        return {"CiphertextBlob": "some_value".encode()}

class FakeBoto(object):
    def client(self, client_name):
        return FakeKms()

handler_impl(event, context, FakeBoto(), FakeHttplib())