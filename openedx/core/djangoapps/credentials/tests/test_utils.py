"""Tests covering Credentials utilities."""
import uuid

from edx_oauth2_provider.tests.factories import ClientFactory
import mock
from nose.plugins.attrib import attr
from provider.constants import CONFIDENTIAL

from openedx.core.djangoapps.credentials.models import CredentialsApiConfig
from openedx.core.djangoapps.credentials.tests.mixins import CredentialsApiConfigMixin
from openedx.core.djangoapps.credentials.utils import get_credentials
from openedx.core.djangoapps.credentials.tests import factories
from openedx.core.djangolib.testing.utils import CacheIsolationTestCase, skip_unless_lms
from student.tests.factories import UserFactory


UTILS_MODULE = 'openedx.core.djangoapps.credentials.utils'


@skip_unless_lms
@attr(shard=2)
@mock.patch(UTILS_MODULE + '.get_edx_api_data')
class TestGetCredentials(CredentialsApiConfigMixin, CacheIsolationTestCase):
    ENABLED_CACHES = ['default']

    def setUp(self):
        super(TestGetCredentials, self).setUp()

        ClientFactory(name=CredentialsApiConfig.OAUTH2_CLIENT_NAME, client_type=CONFIDENTIAL)

        self.create_credentials_config()
        self.user = UserFactory()

    def test_get_many(self, mock_get_edx_api_data):
        expected = factories.UserCredential.create_batch(3)
        mock_get_edx_api_data.return_value = expected

        actual = get_credentials(self.user)

        mock_get_edx_api_data.assert_called_once()
        call = mock_get_edx_api_data.mock_calls[0]
        __, __, kwargs = call

        querystring = {
            'username': self.user.username,
            'status': 'awarded',
        }
        self.assertEqual(kwargs['querystring'], querystring)
        self.assertIsNone(kwargs['resource_id'])

        self.assertEqual(actual, expected)

    def test_get_one(self, mock_get_edx_api_data):
        expected = factories.UserCredential()
        mock_get_edx_api_data.return_value = expected

        program_uuid = str(uuid.uuid4())
        actual = get_credentials(self.user, program_uuid=program_uuid)

        mock_get_edx_api_data.assert_called_once()
        call = mock_get_edx_api_data.mock_calls[0]
        __, __, kwargs = call

        querystring = {
            'username': self.user.username,
            'status': 'awarded',
            'program_uuid': program_uuid,
        }
        self.assertEqual(kwargs['querystring'], querystring)
        self.assertEqual(kwargs['resource_id'], program_uuid)

        self.assertEqual(actual, expected)
