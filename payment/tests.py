import os
from django.conf import settings    
import django.test.TestCase

# overwrite default settings: use local test server
@override_settings(FDS_HOST='localhost')
@override_settings(FDS_USER='test_user')
@override_settings(FDS_PRIVATE_KEY=os.path.join(BASE_DIR, 'test_config', 'keys', 'test_keys'))
@override_settings(FDS_HOST_KEY=os.path.join(BASE_DIR, 'test_config', 'keys', 'test_keys.pub'))
@override_settings(FDS_DATA_PATH=os.path.join(BASE_DIR, 'test_config', 'downloaded_data_files'))
@override_settings(FDS_PORT=22)
class PostFinanceConnectorTest(django.test.TestCase):

    def setUp(self):
        # empty data directory
        for f in os.listdir():
            os.remove(f)

    def test_get_files(self):
        '''Tests FDSConnection.get_files().

        PRE:
        The development server is running.
        '''
        files = os.listdir(sftp-test)
        connection = FDSConnection()
        connection.get_files()
        assert(files == os.listdir(FDS_DATA_PATH))
