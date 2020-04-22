SELECT DISTINCT usr.username,
                usr.first_name,
                usr.last_name,
                subscribe.state,
                course.name                                            as "Course name",
                COALESCE(payment.amount, 0)                            as paid,
                subscribe.price_to_pay,
                (subscribe.price_to_pay - COALESCE(payment.amount, 0)) as diff

FROM courses_subscribe subscribe
         JOIN courses_course course on subscribe.course_id = course.id
         JOIN courses_offering offering on course.offering_id = offering.id
         JOIN courses_period period on offering.period_id = period.id
         JOIN courses_userprofile profile on subscribe.user_id = profile.user_id
         JOIN auth_user usr on profile.user_id = usr.id
         LEFT JOIN payment_subscriptionpayment payment on subscribe.id = payment.subscription_id
         LEFT JOIN payment_payment bank_transaction on payment.payment_id = bank_transaction.id
         LEFT JOIN refund2020 refund on usr.username = refund.username

WHERE offering.name = 'FS2020 Q1'
  AND subscribe.state NOT IN ('rejected')

ORDER BY diff, usr.first_name, usr.last_name
