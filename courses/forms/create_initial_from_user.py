from django.contrib.auth.models import User

from courses.models import StudentStatus


def create_initial_from_user(user: User, initial: dict = None) -> dict:
    data = initial or dict()

    data['first_name'] = user.first_name
    data['last_name'] = user.last_name
    data['gender_options'] = user.profile.gender
    if user.profile.gender not in ["man", "woman", "non-binary"]:
        data['gender_options'] = 'custom'
        data['gender_custom_value'] = user.profile.gender

    data['phone_number'] = user.profile.phone_number
    data['student_status'] = user.profile.student_status != StudentStatus.NO
    data['university'] = user.profile.student_status
    data['legi'] = user.profile.legi
    data['newsletter'] = user.profile.newsletter
    data['get_involved'] = user.profile.get_involved
    data['picture'] = user.profile.picture
    data['about_me'] = user.profile.about_me
    if user.profile.address:
        data['street'] = user.profile.address.street
        data['plz'] = user.profile.address.plz
        data['city'] = user.profile.address.city
    data['email'] = user.email
    data['email_repetition'] = user.email
    data['body_height'] = user.profile.body_height

    data['birthdate'] = user.profile.birthdate
    data['nationality'] = user.profile.nationality
    data['residence_permit'] = user.profile.residence_permit
    data['ahv_number'] = user.profile.ahv_number
    if user.profile.bank_account:
        data['iban'] = user.profile.bank_account.iban
        data['bank_name'] = user.profile.bank_account.bank_name
        data['bank_zip_code'] = user.profile.bank_account.bank_zip_code
        data['bank_city'] = user.profile.bank_account.bank_city
        data['bank_country'] = user.profile.bank_account.bank_country

    return data
