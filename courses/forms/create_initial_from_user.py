def create_initial_from_user(user, initial={}):
    initial['first_name'] = user.first_name
    initial['last_name'] = user.last_name
    initial['gender'] = user.profile.gender
    initial['phone_number'] = user.profile.phone_number
    initial['student_status'] = user.profile.student_status
    initial['legi'] = user.profile.legi
    initial['newsletter'] = user.profile.newsletter
    initial['get_involved'] = user.profile.get_involved
    initial['picture'] = user.profile.picture
    initial['about_me'] = user.profile.about_me
    if user.profile.address:
        initial['street'] = user.profile.address.street
        initial['plz'] = user.profile.address.plz
        initial['city'] = user.profile.address.city
    initial['email'] = user.email
    initial['email_repetition'] = user.email
    initial['body_height'] = user.profile.body_height

    initial['birthdate'] = user.profile.birthdate
    initial['nationality'] = user.profile.nationality
    initial['residence_permit'] = user.profile.residence_permit
    initial['ahv_number'] = user.profile.ahv_number
    if user.profile.bank_account:
        initial['iban'] = user.profile.bank_account.iban
        initial['bank_name'] = user.profile.bank_account.bank_name
        initial['bank_zip_code'] = user.profile.bank_account.bank_zip_code
        initial['bank_city'] = user.profile.bank_account.bank_city
        initial['bank_country'] = user.profile.bank_account.bank_country

    return initial
