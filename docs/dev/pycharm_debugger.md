1.  Open the pycharm settings
2.  In the *Settings / Preferences* dialog go to *Build, Execution, Deployment* and then *Docker*
3.  Click on *+* and then *Apply*
4.  Go to *Project: tq_website*, then *Project Interpreter* and in the *Drop Down Menu* choose *Show All*
5.  Click on the *+* and then *Add Remote*
6.  In the Pop-Up, choose *Docker-Compose*
6.1 Under *Server*, *Docker* should show up (only if you did steps 2. and 3. right)
6.2 *Configuration Files* should show your docker-compose.yml file (if not, are you in the tq_website project?)
6.3 *Service* should have *Django*
7. Apply and close, go back to the main editor. In the right upper corner click on the combo box reading *tq_website*, and then *Edit Configurations*
8. In the pop-up, with the tq_website configuration selected, choose *Host* to be *0.0.0.0*