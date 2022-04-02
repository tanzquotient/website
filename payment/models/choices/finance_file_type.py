from django.utils.translation import gettext_lazy as _


class FinanceFileType:
    POSTFINANCE_XML = 'postfinance_xml'
    ZKB_CSV = 'zkb_csv'

    CHOICES = (
        (POSTFINANCE_XML, _('Postfinance XML')),
        (ZKB_CSV, _('ZKB CSV'))
    )