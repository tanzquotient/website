import logging
import re

from courses.models import Subscribe, PaymentMethod, SubscribeState
from payment.models import Payment, SubscriptionPayment

log = logging.getLogger('payment')

USI_PREFIX = "USI-"
# also accept USL since I is often typed as L
RE_USI_STRICT = re.compile(r"[USILusil]{3,3}[\- _](?P<usi>[a-zA-Z0-9]{6,6})")


class PaymentProcessor:
    def process_payments(self, queryset=Payment.objects):
        self.detect_irrelevant_payments()
        self.match_payments(queryset)
        self.finalize_payments(queryset)

    def detect_irrelevant_payments(self, queryset=Payment.objects):
        new_payments = queryset.filter(state=Payment.State.NEW, credit_debit=Payment.CreditDebit.DEBIT).all()

        for payment in new_payments:
            payment.type = Payment.Type.IRRELEVANT
            payment.save()

    def match_payments(self, queryset=Payment.objects):
        new_payments = queryset.filter(state=Payment.State.NEW, credit_debit=Payment.CreditDebit.CREDIT).all()

        for payment in new_payments:
            if payment.remittance_user_string:
                matches = RE_USI_STRICT.findall(payment.remittance_user_string)

                # if no matches, try removing all spaces first
                if not matches:
                    matches = RE_USI_STRICT.findall(payment.remittance_user_string.replace(" ", ""))

                if matches:
                    payment.type = Payment.Type.SUBSCRIPTION_PAYMENT
                    payment.save()

                    for usi in matches:
                        subscription_query = Subscribe.objects.filter(usi=usi, state=SubscribeState.CONFIRMED)
                        if subscription_query.count() == 1:
                            matched_subscription = subscription_query.first()

                            # check if payment amount sufficient
                            to_pay = matched_subscription.get_price_to_pay()
                            if to_pay is None:
                                log.warning(
                                    "Received payment {} which is related to a course with undefined prices.".format(
                                        payment))
                                payment.state = Payment.State.MANUAL
                                payment.save()
                                break

                            sp = SubscriptionPayment(payment=payment, subscription=matched_subscription,
                                                     amount=to_pay)
                            sp.save()
                            log.info('Matched payment {0} to subscription {1}'.format(payment, subscription_query))
                        elif subscription_query.count() > 1:
                            # should never happen since USI is unique
                            log.error(
                                "Implementation Error: Payment {0} is not related to a unique Subscription".format(
                                    payment))
                            break
                        # elif course_query.count() == 1:
                        #    course = course_query.first()
                        #    log.info("Matched payment to course payment {}".format(course))
                        #    CoursePayment(course=course, payment=payment, amount=payment.amount).save()
                        #    payment.type = payment.Type.COURSE_PAYMENT_TRANSFER
                        #    payment.state = payment.State.PROCESSED
                        #    payment.save()
                        #    break
                        else:
                            log.warning("USI {0} was not found for payment {1}.".format(usi, payment))
                    self._check_balance(payment)
                else:
                    log.info("No USI was recognized in payment {0}.".format(payment))
                    # try to detect if it is a teacher transfer
                    # TODO improve this with a code for teachers when they transfer course payments
                    payment.state = payment.State.MANUAL
                    payment.save()
            else:
                log.warning("No user remittance was found for payment {0}.".format(payment))
                payment.state = Payment.State.MANUAL
                payment.save()

    def finalize_payments(self, queryset=Payment.objects):
        matched_payments = queryset.filter(state=Payment.State.MATCHED).all()

        for payment in matched_payments:
            for s in payment.subscriptions.all():
                s.mark_as_payed(PaymentMethod.ONLINE)
            payment.state = Payment.State.PROCESSED
            payment.save()

    def check_balance(self, payments):
        for payment in payments.filter(state__in=[Payment.State.NEW, Payment.State.MANUAL]).all():
            self._check_balance(payment)

    def _check_balance(self, payment):
        """
        Updates the payment according to currently linked subscriptions.

        Returns true if the payment's amount is equals to the sum of the matched subscriptions.
        """
        if payment.state in [Payment.State.NEW,
                             Payment.State.MANUAL] and payment.type == payment.Type.SUBSCRIPTION_PAYMENT:
            remaining_amount = payment.amount - payment.subscription_payments_amount_sum()

            if remaining_amount == 0:
                payment.state = Payment.State.MATCHED
                payment.amount_to_reimburse = 0
                payment.save()
                return True
            elif remaining_amount > 0:
                payment.amount_to_reimburse = remaining_amount
                payment.state = Payment.State.MANUAL
                payment.save()
                return False
            else:
                payment.state = Payment.State.MANUAL
                payment.save()
                return False
