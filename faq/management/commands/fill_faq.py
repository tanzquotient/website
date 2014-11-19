# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import NoArgsCommand
from faq.models import *

class Command(NoArgsCommand):
    questions=[
               ["Kann ich mich alleine für einen Kurs anmelden?","Einzelanmeldungen sind immer willkommen! Wir versuchen gerne, Tanzpartner für Einzelpersonen zu finden. Frühe Anmeldungen geben uns Zeit, mögliche Tanzpartner anzufragen und erhöhen somit die Erfolgswahrscheinlichkeit ;)"],
               ["Bin ich während den Tanzkursen über den TQ versichert?","Normalerweise passiert beim Tanzen nichts schlimmes. Für den Fall, dass dennoch etwas passiert: Versicherung ist Sache der Teilnehmenden. Die TQ-Angebot-Nutzenden sind NICHT über den TQ versichert."],       
               ["Wann kann ich mich für einen Kurs anmelden?","Der TQ hat jedes Semester zwei Kursperioden à 6 Wochen. Die erste Kursperiode beginnt in der zweiten Semesterwoche, die zweite im der achten Semesterwoche. Wir versuchen, die Anmeldungen zwei Wochen vor Kursbeginn zu öffnen. Die Anmeldungen schliessen jeweils einen Tag vor Kursbeginn, nachträgliche Anmeldungen könenn nicht berücksichtigt werden."],   
               ["Wie kann ich mich wieder vom Kurs abmelden?","Eine Abmeldung ist bis am Tag vor Kursbeginn möglich. Danach werden die vollen Kurskosten in Rechnung gestellt. "],   
               ["Wie funktioniert die Bezahlung der Kurse?","Das Kursgeld muss am ersten Kurstag passend in den Kurs mitgebracht werden und wird von den Tanzlehrern eingesammelt. Die Begleichung der Kurskosten an einem späteren Kurstag ist nicht möglich. Alle Teilnehmer, die am ersten Kurstag verhindert sind, bekommen eine Rechnung zugeschickt. "],   
               ["Muss ich spezielle Kleidung mitbringen?","Generell ist es kein Problem, in normaler Strassenkleidung zu tanzen. Bei den Schuhen sind jedoch Ledersohlen empfehlenswert, Tanzen in Socken ist ebenfalls möglich."],   
               ["Wann finden welche Kursstufen statt?","In der ersten Semesterhälfte gibt es normalerweise Kurse der Stufen I und III, in der zweiten Semesterhälfte die Fortsetzungskurse (II/IV). Es ist jedoch möglich, dass wir bei grosser Nachfrage ausserplanmässige Kurse durchführen."],   
               ["Wie viele Kursstufen gibt es?","Die regulären Kurse gehen über vier Stufen, die du innerhalb eines Jahres besuchen kannst. Falls du alles Stufen absolviert hast und beim TQ weitertanzen möchtest, gibt es die Möglichkeit, sich einer Gruppe anzuschliessen oder selbst eine zu gründen."],   
               ["Kann ich für den TQ unterrichten?","Natürlich! Wir sind immer auf der Suche nach neuen Tanzlehrern. Melde dich bei Marie (Tanzadministration), sie hilft dir gerne weiter."],   
               ["Wie kann ich mich beim TQ engagieren?","Wir sind immer auf der Suche nach freiwilligen Helfern. Abhängig von der Zeit, die du investieren möchtest, haben wir verschiedenste Jobs anzubieten. Melde dich doch einfach mal unverbindlich bei Irina, unserer Präsidentin."],   
               ["Kann ich mich ohne Erfahrung für Kurs II anmelden?","Falls du keine Erfahrung im entsprechenden Tanz hast, ist eine Anmeldung für Kurs II nicht möglich. Bitte warte bis zum Anfang des nächsten Semesters, dann wird es wieder einen Kurs I geben."],   
               ["Welche Tänze bietet der TQ an?","Standardmässig haben wir Salsa (cubana/puertorriqueña), Tango Argentino, Lindy Hop und Social im Angebot. Für alle, die noch unentschlossen sind, bieten wir jeweils freitagabends Gratiskurse im ASVZ Hönggerberg an."],   
    ]
    
    def handle_noargs(self, **options):
        group = QuestionGroup.objects.get_or_create(name='main_faq')[0]
        
        for q in self.questions:
            Question.objects.get_or_create(question_text=q[0], defaults={'answer_text': q[1], 'question_group': group})
