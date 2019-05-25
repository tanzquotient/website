from collections import OrderedDict


class Residence:
    PERMITS = OrderedDict()
    PERMITS['SWISS'] = 'Swiss citizen'
    PERMITS['B'] = 'B EU/EFTA permit (Resident foreign nationals)'
    PERMITS['C'] = 'C EU/EFTA permit (Settled foreign nationals)'
    PERMITS['Ci'] = 'Ci EU/EFTA permit (Resident foreign nationals with gainful employment)'
    PERMITS['L'] = 'L EU/EFTA permit (Short-term residents)'
    PERMITS['G'] = 'G EU/EFTA permit (Cross-border commuters)'
    PERMITS['F'] = 'Permit F (provisionally admitted foreigners)'
    PERMITS['N'] = 'Permit N (permit for asylum-seekers)'
    PERMITS['S'] = 'Permit S (people in need of protection)'
    PERMITS['<NO>'] = 'Short-term stay without VISA'

    CHOICES = list(PERMITS.items())
