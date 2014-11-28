# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import NoArgsCommand
from courses.models import *
from django.contrib.auth.models import User, Group, Permission

import datetime

class Command(NoArgsCommand):
    style_names = ['Walzer','Discofox','Foxtrott','Quick-Step','Jive','Rumba','Tango','Salsa Cubana',u'Salsa Puertorriqueña','Bachata','Lindy Hop','Zouk']
    course_names = ['Discofox','Social','Tango','Salsa Cubana',u'Salsa Puertorriqueña','Bachata','Lindy Hop','Zouk']
    room_names = ['CAB Foodlab','GEP/Alumni-Pavillon','HXE','Raum der Stille',u'ASVZ Hönggerberg Arena 3',u'PH, LAC-C014']
    room_desc = ['Das foodLAB ist das DSR Restaurant im CAB. Es befindet sich im obersten Stock direkt über dem Haupteingang. Die Treppe hoch, dann gerade aus. Auf der rechten Seite geht eine Metalltreppe in den obersten Stock. Oder nach dem Haupteingang gerade nach hinten laufen, dann links den Lift ins oberste Stockwerk.',
                     'Das GEP befindet sich zwischen der Polybahn und der Cafeteria. Der Eingang ist auf der Seite der Polyterasse.',
                     'In Richtung Stadt auf ist das HXE auf der rechten Seite der Strasse. Der Eingang ist auf der Seite, gleich da, wo die Rampe zu Ende ist. Der Tanzraum ist direkt hinter der Tür rechts.',
                     'Der Raum der Stille befindet sich im HPI auf dem Hönggerberg. Dies ist das Gebäude in dem sich auch das Bistro und der Coop befinden. Der Eingang befindet sich auf der Rückseite des Gebäudes. Von der Bushaltestelle aus um das Gebäude herum gehen. Die Tür sieht aus wie ein Hintereingang, ist aber richtig. Der Raum der Stille befindet sich im D-Stock (ein Stock runter).',
                     'Die Arena 3 ist das Tanzstudio des ASVZ auf dem Hönggerberg. Von der Bushaltestelle aus rechts am HPH vorbei. Im Gebäude die Treppe runter (Legi wird hier kontrolliert), dann links. An der Turnhalle vorbei, bis an das Ende des Gang. Hier die Treppe nach oben. Die Arena 3 ist der erste Raum auf der linken Seite.<br/><b>Wichtig: Bitte nehmt ein Schloss mit, und schliesst eure Sachen ein. Aus feuerpolizeilichen Gründen dürfen im und vor dem Raum KEINE Taschen herumstehen!</b>',
                     u'Im Hauptbahnhof Zürich den Ausgang "Europaallee" benutzen. Zugang über Treppe zu den Gebäuden LAA, LAB und LAC oder via Kasernenstrasse zum Gebäude LAD. Für Anreise mit Tram und Bus: Tram 3 und 14 oder Bus 31 bis Haltestelle "Sihlpost", dann nach dem Transa-Shop rechts die Treppe zur PH nehmen.',
                     ]
    room_url = ['https://www.google.ch/maps/place/ETHZ+CAB,+8006+Z%C3%BCrich/@47.3775785,8.5486153,17z/data=!3m1!5s0x479aa0a661fe00ab:0x3f31372993b75a8e!4m7!1m4!3m3!1s0x479aa0a62c4b4f21:0xb86c4ed668042726!2sAlumni+Pavillon,+8001+Z%C3%BCrich!3b1!3m1!1s0x479aa0a661c27a25:0x8fc386de863192d0',
                'https://www.google.ch/maps/place/Alumni+Pavillon,+8001+Z%C3%BCrich/@47.3766703,8.5464373,17z/data=!4m2!3m1!1s0x479aa0a62c4b4f21:0xb86c4ed668042726',
                'https://www.google.ch/maps/place/HXE,+8049+Z%C3%BCrich/@47.4074323,8.5062816,17z/data=!3m1!4b1!4m2!3m1!1s0x47900a5512a879b9:0xc7bafd63eb1efe8f',
                'https://www.google.ch/maps/place/HPI,+8049+Z%C3%BCrich/@47.4083897,8.5079978,19z/data=!3m1!4b1!4m7!1m4!3m3!1s0x47900a5512a879b9:0xc7bafd63eb1efe8f!2sHXE,+8049+Z%C3%BCrich!3b1!3m1!1s0x47900a558648464b:0x331749ef430526d1',
                'https://www.google.ch/maps/place/HPS,+Schafmattstrasse+33,+8093+Z%C3%BCrich/@47.406886,8.5113617,18z/data=!3m1!4b1!4m2!3m1!1s0x47900a566b8d1b43:0x279b244f40c6e7ca',
                'https://www.google.ch/maps/place/Geb%C3%A4ude+LAC,+Europaallee,+8004+Z%C3%BCrich/@47.3778591,8.5338249,19z/data=!3m1!4b1!4m5!1m2!2m1!1sPH!3m1!1s0x47900a0f908d701d:0x195225583d7d9336',
                ]
    
    def handle_noargs(self, **options):
        vorstand = Group.objects.create(name='Vorstand')
        
        user =User.objects.create_user('simon', 'siwehrli@student.ethz.ch', 'a', first_name="Simon", last_name="Wehrli")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        vorstand.user_set.add(user)
        user=User.objects.create_user('irina', None, 'i', first_name="Irina", last_name="Ritsch")
        user.is_staff = True
        user.save()
        vorstand.user_set.add(user)
        User.objects.create_user('matthäus', None, 'm', first_name="Matthäus", last_name="Geiger")
        user.is_staff = True
        user.save()
        vorstand.user_set.add(user)
        User.objects.create_user('hendrik', None, 'h', first_name="Hendrik", last_name="Spanke")
        user.is_staff = True
        user.save()
        vorstand.user_set.add(user)
        User.objects.create_user('julian', None, 'j', first_name="Julian", last_name="Böhler")
        user.is_staff = True
        user.save()
        vorstand.user_set.add(user)
        User.objects.create_user('marie', None, 'm', first_name="Marie", last_name="Andrä")
        user.is_staff = True
        user.save()
        vorstand.user_set.add(user)
        User.objects.create_user('kelsey', None, 'k', first_name="Kelsey", last_name="Schärer")
        user.is_staff = True
        user.save()
        vorstand.user_set.add(user)
        vorstand.save()
        
        for p in Permission.objects.all():
            vorstand.permissions.add(p)
        
        for style_name in self.style_names:
            Style.objects.get_or_create(name=style_name, defaults={'url_info': "http://de.wikipedia.org/wiki/{}".format(style_name)})
        Style.objects.get_or_create(name="Discofox", defaults={'url_info': "http://de.wikipedia.org/wiki/{}".format("Discofox")})
        for course_name in self.course_names:
            for i in range(1, 6):
                n=u"{} {}".format(course_name, i)
                CourseType.objects.get_or_create(name=n, defaults={'level': i})
        d = CourseType.objects.get(name='Discofox 1')
        d.styles = [Style.objects.get(name='Walzer'),Style.objects.get(name='Tango'),Style.objects.get(name='Jive'),Style.objects.get(name='Discofox')]
        d.save()
  
        for i,room_name in enumerate(self.room_names):
            Room.objects.get_or_create(name=room_name, defaults={'description': self.room_desc[i],'url': self.room_url[i]})
        
        pHS14q1 = Period.objects.get_or_create(date_from=datetime.date(2014,9,15), date_to=datetime.date(2014,10,31))[0]
        pHS14q2 = Period.objects.get_or_create(date_from=datetime.date(2014,11,2), date_to=datetime.date(2014,12,19))[0]
        pFS15q1 = Period.objects.get_or_create(date_from=datetime.date(2015,2,16), date_to=datetime.date(2015,4,2))[0]
        pFS15q2 = Period.objects.get_or_create(date_from=datetime.date(2015,4,13), date_to=datetime.date(2015,5,29))[0]
        pHS15q1 = Period.objects.get_or_create(date_from=datetime.date(2015,9,14), date_to=datetime.date(2015,10,30))[0]
        pHS15q2 = Period.objects.get_or_create(date_from=datetime.date(2015,11,1), date_to=datetime.date(2015,12,18))[0]
        pFS16q1 = Period.objects.get_or_create(date_from=datetime.date(2016,2,22), date_to=datetime.date(2016,3,24))[0]
        pFS16q2 = Period.objects.get_or_create(date_from=datetime.date(2016,4,4), date_to=datetime.date(2016,6,3))[0]
        o = Offering.objects.get_or_create(name="HS 2014 Q1", defaults={'period': pHS14q1, 'display': True, 'active': True})[0]
        Offering.objects.get_or_create(name="HS 2014 Q2", defaults={'period': pHS14q2, 'display': True, 'active': True})
        Offering.objects.get_or_create(name="FS 2015 Q1", defaults={'period': pFS15q1, 'display': False, 'active': False})
        Offering.objects.get_or_create(name="FS 2015 Q2", defaults={'period': pFS15q2, 'display': False, 'active': False})
        Offering.objects.get_or_create(name="HS 2015 Q1", defaults={'period': pHS15q1, 'display': False, 'active': False})
        Offering.objects.get_or_create(name="HS 2015 Q2", defaults={'period': pHS15q2, 'display': False, 'active': False})
        Offering.objects.get_or_create(name="FS 2016 Q1", defaults={'period': pFS16q1, 'display': False, 'active': False})
        Offering.objects.get_or_create(name="FS 2016 Q2", defaults={'period': pFS16q2, 'display': False, 'active': False})

        c = Course.objects.get_or_create(name="Salsa Cubana 5",defaults={'type': CourseType.objects.get(name='Salsa Cubana 5'), 'offering': o, 'room': Room.objects.get(name=self.room_names[0])})[0]
        CourseTime.objects.get_or_create(course = c, defaults={'weekday': 'mon', 'time_from': datetime.time(15,00), 'time_to': datetime.time(16,00)})
        c.type.styles.add(Style.objects.get(name='Salsa Cubana'))
        
        c = Course.objects.get_or_create(name="Social 3",defaults={'type': CourseType.objects.get(name='Social 3'), 'offering': o, 'room': Room.objects.get(name=self.room_names[1])})[0]
        CourseTime.objects.get_or_create(course = c, defaults={'weekday': 'mon', 'time_from': datetime.time(16,00), 'time_to': datetime.time(17,30)})
        c.type.styles.add(Style.objects.get(name='Jive'))
        c.type.styles.add(Style.objects.get(name='Discofox'))
        c.type.styles.add(Style.objects.get(name='Foxtrott'))
        c.type.styles.add(Style.objects.get(name='Walzer'))
        c.type.styles.add(Style.objects.get(name='Rumba'))
        
        c=Course.objects.get_or_create(name="Bachata 3",defaults={'type': CourseType.objects.get(name='Bachata 3'), 'offering': o, 'room': Room.objects.get(name=self.room_names[2])})[0]
        CourseTime.objects.get_or_create(course = c, defaults={'weekday': 'thu', 'time_from': datetime.time(18,15), 'time_to': datetime.time(19,00)})
        
        c = Course.objects.get_or_create(name="Lindy Hop 1",defaults={'type': CourseType.objects.get(name='Lindy Hop 1'), 'offering': o, 'room': Room.objects.get(name=self.room_names[3])})[0]
