import logging
from time import sleep

from post_office import mail
from post_office.lockfile import FileLock, FileLocked, default_lockfile
from post_office.settings import get_log_level
from django.db import connection

from tq_website import settings

logger = logging.getLogger("tq")


def send_queued_emails() -> None:
    batches_per_second = settings.EMAILS_RATE_LIMIT
    try:
        with FileLock(default_lockfile):
            logger.info(
                "Acquired lock for sending queued emails at %s.lock", default_lockfile
            )
            batch_count = 0
            while True:
                try:
                    queued_emails = list(mail.get_queued())
                    mail.attach_templates(queued_emails)
                    if queued_emails:
                        total_sent, total_failed, total_requeued = mail._send_bulk(
                            emails=queued_emails,
                            uses_multiprocessing=False,
                            log_level=get_log_level(),
                        )
                        logger.info(
                            "%s emails attempted, %s sent, %s failed, %s requeued",
                            len(queued_emails),
                            total_sent,
                            total_failed,
                            total_requeued,
                        )
                        batch_count += 1
                        if batch_count >= batches_per_second:
                            batch_count = 0
                            sleep(1)
                except Exception as e:
                    logger.exception(e, extra={"status_code": 500})
                    raise

                connection.close()

                if not mail.get_queued().exists():
                    break
    except FileLocked:
        logger.info("Failed to acquire lock, terminating now.")
