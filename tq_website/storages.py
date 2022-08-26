from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class TqStorage(S3Boto3Storage):

    def __init__(self, bucket_name, host, port, region, use_ssl, custom_domain,
                 access_key, secret_key, querystring_auth=True) -> None:
        config = dict(
            use_ssl=use_ssl,
            url_protocol='https:' if use_ssl else 'http:',
            access_key=access_key,
            secret_key=secret_key,
            region_name=region,
            querystring_auth=querystring_auth,
        )
        if custom_domain:
            config['custom_domain'] = custom_domain.format(bucket_name)
        else:
            protocol = 'https' if use_ssl else 'http'
            config['endpoint_url'] = "{}://{}:{}".format(protocol, host, port)
        super().__init__(bucket_name=bucket_name, **config)


class MediaStorage(TqStorage):
    def __init__(self) -> None:
        super().__init__(
            bucket_name=settings.S3_MEDIA_BUCKET,
            host=settings.S3_MEDIA_HOST,
            port=settings.S3_MEDIA_PORT,
            region=settings.S3_MEDIA_REGION,
            use_ssl=settings.S3_MEDIA_USE_SSL,
            custom_domain=settings.S3_MEDIA_CUSTOM_DOMAIN,
            access_key=settings.S3_MEDIA_ACCESS_KEY,
            secret_key=settings.S3_MEDIA_SECRET_KEY,
            querystring_auth=True,
        )


class StaticStorage(TqStorage):
    def __init__(self) -> None:
        super().__init__(
            bucket_name=settings.S3_STATIC_BUCKET,
            host=settings.S3_STATIC_HOST,
            port=settings.S3_STATIC_PORT,
            region=settings.S3_STATIC_REGION,
            use_ssl=settings.S3_STATIC_USE_SSL,
            custom_domain=settings.S3_STATIC_CUSTOM_DOMAIN,
            access_key=settings.S3_STATIC_ACCESS_KEY,
            secret_key=settings.S3_STATIC_SECRET_KEY,
            querystring_auth=False,
        )


class FinanceStorage(TqStorage):
    def __init__(self) -> None:
        super().__init__(
            bucket_name=settings.S3_FINANCE_BUCKET,
            host=settings.S3_FINANCE_HOST,
            port=settings.S3_FINANCE_PORT,
            region=settings.S3_FINANCE_REGION,
            use_ssl=settings.S3_FINANCE_USE_SSL,
            custom_domain=settings.S3_FINANCE_CUSTOM_DOMAIN,
            access_key=settings.S3_FINANCE_ACCESS_KEY,
            secret_key=settings.S3_FINANCE_SECRET_KEY,
            querystring_auth=True,
        )
