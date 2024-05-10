# Email templates

We use Post Office for sending emails.
It generates emails from templates stored in the database ([admin panel][admin]).

This directory contains the templates for the important emails that are sent by
Python code, i.e., whose template name is referenced by some Python code.
This allows:

- easier grepping for a template name and variables used in a template
- easier mass editing
- version control

Thus the workflow is currently (May 2024) as follows:

1. Update the templates in this directory
2. Get it PR-reviewed for quality
3. Manually copy the changes into the [admin panel][admin]

That is, THIS directory is the source of truth.
But the database is what prod will use to send emails.

This directory only contains emails that are actively used and maintained.
The database also contains older templates that are not used anymore.

Historically, there was also a Google doc where the communications team worked
on some improvements ([link][gdoc]).

[admin]: https://tanzquotient.org/en/admin/post_office/emailtemplate/
[gdoc]: https://docs.google.com/document/d/1GbiAhNGGBuLzRJ9yZA_tugcOby1pGMxhDnZlJfGeeDw/edit#heading=h.ew6hgrsufbw1

