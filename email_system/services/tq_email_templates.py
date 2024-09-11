from dataclasses import dataclass
from django.template import Context, Template
from django.template.loader import render_to_string, TemplateDoesNotExist
from typing import Optional, Tuple


@dataclass
class TqEmailTemplate:
    name: str
    subject_de: str
    subject_en: str

    def render(
        self, context: Optional[dict]
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Tries to find the given template in the "email_templates" directory.
        A plaintext email and/or HTML email may exist.
        Uses the context to render the template(s).

        Returns:

        - the subject
        - the plaintext email
        - the HTML email
        """

        try:
            plaintext = render_to_string(f"{self.name}.txt", context)
        except TemplateDoesNotExist:
            plaintext = None

        try:
            html = render_to_string(f"{self.name}.html", context)
        except TemplateDoesNotExist:
            html = None

        # TODO: translates (use the language stored for the user in their profile)
        subject = Template(self.subject_en).render(Context(context))

        return subject, plaintext, html


PAYMENT_REMINDER = TqEmailTemplate(
    "payment_reminder",
    "Zahlungserinnerung {{ course }}",
    "Payment Reminder {{ course }}",
)
