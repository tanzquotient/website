import logging
from io import StringIO

from django.core.files.base import ContentFile
from paramiko import RSAKey
from paramiko.client import SSHClient, AutoAddPolicy

from payment.models import FinanceFile
from payment.models.choices import FinanceFileType
from tq_website.settings import FDS_PORT, FDS_HOST, FDS_PRIVATE_KEY, FDS_USER

log = logging.getLogger('payment')


class FDSConnection:
    def __init__(self) -> None:
        private_key = RSAKey.from_private_key(StringIO(FDS_PRIVATE_KEY))
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(FDS_HOST, username=FDS_USER, pkey=private_key, port=FDS_PORT)
        self.sftp = self.client.open_sftp()
        log.info("Connected to FDS")

    def get_files(self) -> None:
        log.info("Receiving files from FDS...")

        # Iterate over all remote files
        self.sftp.chdir('yellow-net-reports')
        filenames = self.sftp.listdir()
        log.info("Found {} files on server".format(filenames))
        for filename in filenames:
            if not FinanceFile.objects.filter(name=filename).exists():
                log.info("Receiving {}".format(filename))
                with self.sftp.open(filename) as file:
                    content = file.read()
                if isinstance(content, str):
                    content = content.encode('utf-8')
                content_file = ContentFile(content)
                db_file = FinanceFile.objects.create(name=filename, type=FinanceFileType.POSTFINANCE_XML)
                db_file.file.save(filename, content_file)
                log.info("Saved {}".format(filename))
            else:
                log.info("Skipping already existing file: {}".format(filename))
