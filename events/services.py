from django.shortcuts import get_object_or_404

from courses.utils import export
from events.models import Event


def export_registrations(event_ids, export_format):

    export_data = []
    for event_id in event_ids:
        event = get_object_or_404(Event, pk=event_id)
        registrations = event.registrations

        data = [['First name', 'Last name', 'Address', 'Email', 'Phone']]

        for r in registrations:
            data.append([
                r.user.first_name,
                r.user.last_name,
                str(r.user.profile.address),
                r.user.email,
                r.user.profile.phone_number
            ])

        export_data.append({'name': event.get_name(), 'data': data})

    if len(export_data) == 0:
        return None

    if len(export_data) == 1:
        event_name = export_data[0]['name']
        return export(export_format, title='Registrations-{}'.format(event_name), data=export_data[0]['data'])

    return export(export_format, title="Registrations", data=export_data, multiple=True)
