I get "INTERNAL SERVER ERROR", but neither Sentry nor the log files notice it!
==============================================================================

Background
----------

This has already occurred once. In fact, the bug was reported by a teacher on 2018-04-08. The corresponding issue was #184. It was fixed on 2018-04-17 after hours of debugging (commit 945a8839f679951277c5d53c2311267a699c48c3).

Debugging process
-----------------

Since no error message was generated, debugging had to be done manually:

- The error could not be reproduced on a development server (it only occurred for a few courses), so code modifications were performed on the production server **AFTER PERFORMING A BACKUP**. The changes were copied to a developer machine and committed, then deleted on the server to get in a consistent state. Then, the solution was pulled from the repo.
- Debugging was done in the following way:

  Different messages were printed to the browser by return them as the message to an :code:`HttpResponse` object.

Solution
--------

Debugging made it clear that the error did not come from the view. Commenting out different lines of code indicated that the part where the filename was set lead to the error. The reason was the following:

In that course period, the people from dance administration used German Umlaut characters (ü, ä, ö) in the course name.

Example: :code:`Social 2(Axel) früh (FS2018 Q2)`

Since the filename of the file to be downloaded should not contain such characters, an error was thrown.

It was then easy to fix the error by simply converting the Umlauts to their corresponding ASCII form (Ex.: ü --> ue)
