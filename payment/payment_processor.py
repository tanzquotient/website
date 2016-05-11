from payment.models import Payment
from courses.models import Subscribe, PaymentMethod
import re
import logging
log = logging.getLogger('payment')


class PaymentProcessor:

    def match_payments(self):
        new_payments = Payment.objects.filter(state=Payment.State.NEW).all()

        prog = re.compile(r".*#(?P<usi>[a-zA-Z0-9]{6,6}).*")
        for payment in new_payments:
            if payment.remittance_user_string:
                match_obj = prog.match(payment.remittance_user_string)
                if match_obj is not None:
                    usi = match_obj.group('usi')
                    subscription_query = Subscribe.objects.filter(usi=usi)
                    if subscription_query.count() == 1:
                        matched_subscription = subscription_query.first()
                        payment.subscription = matched_subscription
                        payment.state = Payment.State.MATCHED
                        matched_subscription.mark_as_payed(PaymentMethod.ONLINE)
                        log.info('Matched payment {0} to subscription {1}'.format(payment, subscription_query))
                        payment.save()
                    elif subscription_query.count() > 1:
                        log.warning("Payment {0} is not related to a unique Subscription".format(payment))
                    else:
                        log.error("USI #{0} was not found for payment {1}.".format(usi, payment))
                else:
                    log.warning("No USI was recognized in payment {0}.".format(payment))
            else:
                log.warning("No user remittance was found for payment {0}.".format(payment))