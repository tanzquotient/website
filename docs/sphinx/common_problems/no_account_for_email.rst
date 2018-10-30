Enrollment error: No account for email (though the account exists)
==================================================================

This issue stems from an old version of the website: There, it was possible to
enrol to a course without having an account. The website then internally created
an account for the subscription. That lead to multiple acocunts per email address, which seems to break allauth,
the authentication plugin we're using.

Solution: Make all users that have the same email address inactive but one.
Do this by clocking on "tanzquotient.org" in the admin bar, then "users..." and search for the email address.
Then mark the accounts you want to inactivate (policy: the surviving account should be the one with the most recent "last logged in" field),
then select "Make inactive" in the dropdown actions list.
