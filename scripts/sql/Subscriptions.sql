SELECT DISTINCT
    user.first_name,
    user.last_name,
    profile.phone_number,
    user.email,
    course.name as "Course name",
    subscribe.usi /*,
    subscribe.state,
    subscribe.paymentmethod*/


FROM courses_subscribe subscribe
         JOIN courses_course course on subscribe.course_id = course.id
         JOIN courses_offering offering on course.offering_id = offering.id
         JOIN courses_period period on offering.period_id = period.id
         JOIN courses_userprofile profile on subscribe.user_id = profile.user_id
         JOIN auth_user user on profile.user_id = user.id

WHERE
        offering.name = 'FS2020 Q1' AND
    /*subscribe.state NOT IN ('rejected')*/
        subscribe.state = 'payed'

ORDER BY user.first_name, user.last_name