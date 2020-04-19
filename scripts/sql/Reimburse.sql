SELECT max(usr.first_name)                                            as first_name,
       max(usr.last_name)                                             as last_name,
       max(refund.name)                                               as name_bank_account,
       max(refund.iban)                                               as iban,
       string_agg(course.name, ', ')                                  as courses,
       string_agg(subscribe.usi, ', ')                                as usi,
       COALESCE(sum(payment.amount), 0) - sum(subscribe.price_to_pay) as to_refund

FROM courses_subscribe subscribe
         JOIN courses_course course on subscribe.course_id = course.id
         JOIN courses_offering offering on course.offering_id = offering.id
         JOIN auth_user usr on usr.id = subscribe.user_id
         JOIN refund2020 refund on refund.username = usr.username
         LEFT JOIN payment_subscriptionpayment payment on subscribe.id = payment.subscription_id

WHERE offering.name = 'FS2020 Q1'
  AND subscribe.state NOT IN ('rejected')
  AND refund.refund_type = 'Bank transfer'

GROUP BY usr.username
HAVING COALESCE(sum(payment.amount), 0) > sum(subscribe.price_to_pay)

ORDER BY first_name, last_name
