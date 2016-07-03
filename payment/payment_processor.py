from payment.models import Payment, SubscriptionPayment
from courses.models import Subscribe, PaymentMethod
import re
import logging

log = logging.getLogger('payment')


class PaymentProcessor:
    def match_payments(self, queryset=Payment.objects):
        new_payments = queryset.filter(state=Payment.State.NEW).all()

        prog = re.compile(r"#(?P<usi>[a-zA-Z0-9]{6,6})")
        for payment in new_payments:
            if payment.remittance_user_string:
                matches = prog.findall(payment.remittance_user_string)
                if matches:
                    payment.type = Payment.Type.SUBSCRIPTION_PAYMENT

                    remaining_amount = payment.amount
                    for usi in matches:
                        subscription_query = Subscribe.objects.filter(usi=usi)
                        if subscription_query.count() == 1:
                            matched_subscription = subscription_query.first()

                            # check if payment amount sufficient
                            to_pay = matched_subscription.get_price_to_pay()
                            if to_pay is None:
                                log.warning(
                                    "Received payment {} which is related to a course with undefined prices.".format(
                                        payment))
                                payment.state = Payment.State.MANUAL
                                break
                            if to_pay <= remaining_amount:
                                sp = SubscriptionPayment(payment=payment, subscription=matched_subscription,
                                                         amount=to_pay)
                                sp.save()
                                remaining_amount -= to_pay
                                matched_subscription.mark_as_payed(PaymentMethod.ONLINE)
                            log.info('Matched payment {0} to subscription {1}'.format(payment, subscription_query))
                        elif subscription_query.count() > 1:
                            # should never happen since USI is unique
                            log.error("Implementation Error: Payment {0} is not related to a unique Subscription".format(payment))
                            break
                        else:
                            log.warning("USI #{0} was not found for payment {1}.".format(usi, payment))
                            payment.state = Payment.State.MANUAL
                            break
                    payment.amount_to_reimburse = remaining_amount
                    if payment.state == Payment.State.NEW:
                        if remaining_amount == 0:
                            payment.state = Payment.State.DONE
                        else:
                            payment.state = Payment.State.MANUAL
                else:
                    log.info("No USI was recognized in payment {0}.".format(payment))
                    # try to detect if it is a teacher transfer
                    # TODO improve this with a code for teachers when they transfer course payments
                    if payment.amount >= 200:
                        payment.type = payment.Type.IRRELEVANT
                        payment.state = payment.State.PROCESSED
                    else:
                        payment.state = payment.State.MANUAL
            else:
                log.info("No user remittance was found for payment {0}.".format(payment))
                payment.state = Payment.State.MANUAL
            payment.save()
