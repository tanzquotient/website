=============================
Infrastructure & Architecture
=============================

Python packages
===============
This page contains information about all the Python packages that are used somewhere in the TQ website. Please keep the information up to date and extend it as new features are added. This makes it easier for newcomers to understand what is going on in the project.

Keep in mind that if the person who implemented a feature is not available anymore, this page is the only reliable source of information about the dependencies.

========================    ==========================================    ===================================================================================================    ===============================================    ======================================
     Package name            version (date of last check for updates)       Purpose of the package                                                                                           Dependencies                              Need exactly version x (reason?)
========================    ==========================================    ===================================================================================================    ===============================================    ======================================
django-ical                 1.4 (26.08.2017)                                iCal calendar syncronisation                                                                             Django>=1.3.4, icalendar>=3.1, pytz                        x
pylint                      1.7.2 (26.08.2017)                              Rate quality of code and check `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ compliance            isort>=4.2.5, six, mccabe, astroid>=1.5.1                  x
graphviz                    0.8 (26.08.2017)                                Write UML diagrams in good graphics formats, e. g. png                                                   x                                                          x
python-dotenv               0.8.2 (04.06.2018)                              Needed for ReadTheDocs.org                                                                               ?                                                          x
sphinx-automodapi           0.7 (04.06.2018)                                Generate summary of entire modules                                                                       ?                                                          x
========================    ==========================================    ===================================================================================================    ===============================================    ======================================
