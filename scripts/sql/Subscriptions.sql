SELECT DISTINCT
    user.first_name,
    user.last_name,
    profile.phone_number,
    user.email,
    course.name as "Course name",
    subscribe.usi,
    IFNULL(payment.amount, 0) as "paid",
    subscribe.price_to_pay,
    (subscribe.price_to_pay - IFNULL(payment.amount, 0)) as diff

FROM courses_subscribe subscribe
    JOIN courses_course course on subscribe.course_id = course.id
    JOIN courses_offering offering on course.offering_id = offering.id
    JOIN courses_period period on offering.period_id = period.id
    JOIN courses_userprofile profile on subscribe.user_id = profile.user_id
    JOIN auth_user user on profile.user_id = user.id
    LEFT JOIN payment_subscriptionpayment payment on subscribe.id = payment.subscription_id
    LEFT JOIN payment_payment bank_transaction on payment.payment_id = bank_transaction.id

WHERE offering.name = 'FS2020 Q1'
    AND subscribe.state NOT IN ('rejected')
    AND (paymentmethod IS NULL OR  paymentmethod <> 'voucher')
    AND (subscribe.price_to_pay - IFNULL(payment.amount, 0)) <> 0

ORDER BY diff, user.first_name, user.last_name
