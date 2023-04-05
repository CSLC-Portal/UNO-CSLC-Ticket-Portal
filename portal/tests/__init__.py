
# NOTE: We need an __init__.py file so that the folder is treated as a module for pytest

from msal import ConfidentialClientApplication

# We'll implement some mock objects here that might be needed by the tests

class MockConfidentialClientApplication(ConfidentialClientApplication):
    MOCK_NAME = 'Some User'
    MOCK_EMAIL = 'someuser@email.com'
    MOCK_OID = '00000000-0000-0000-0000-000000000000'

    def acquire_token_by_auth_code_flow(self, auth_code_flow, auth_response, scopes=None, **kwargs):
        """Override the acqure token function to return a mock token as would be returned from the actual library"""

        tokens = {
            'id_token_claims': {
                'exp': '0',
                'upn': 'test_user_1_',
                'oid': MockConfidentialClientApplication.MOCK_OID,
                'name': MockConfidentialClientApplication.MOCK_NAME,
                'preferred_username': MockConfidentialClientApplication.MOCK_EMAIL
            },
        }

        return tokens
