
"""
This file contains convertion functions from internal
:class:`dedoelen.core.models.Voorstelling` instances to :class:`icalendar.Event`
instances and vice versa.
"""

import datetime
import icalendar

from dedoelen.core.conf import settings
from dedoelen.core.models import Voorstelling

def voorstelling2event(voorstelling):
    """
        Convert a :class:`dedoelen.core.models.Voorstelling` instance to an
        :class:`icalendar.Event` instance. The uid of the event is the hash of
        the event URL. Hence, we assume that if the event changes, the URL stays
        the same. This allows us to update an event in the calendar by changing
        everything, but keeping the same UID ensures the calendar application
        can still identify the event as merely changed (not added new). When an
        event is changed the sequence must be increased.

        :param voorstelling: event in De Doelen
        :type voorstelling: :class:`dedoelen.core.models.Voorstelling`
        :returns: ICS event for the event
        :rtype: :class:`icalender.Event`
    """
    event = icalendar.Event()
    event.add('summary', voorstelling.title)
    event.add('dtstart', voorstelling.tstart)
    event.add('dtend', voorstelling.tend)
    event.add('dtstamp', datetime.datetime.now(settings.AMSTERDAM))
    event['uid'] = str(hash(voorstelling.link))+'@doelenics.nl'
    event.add('last-modified', datetime.datetime.now(settings.AMSTERDAM))
    event.add('description', '\n'.join([voorstelling.description,
        voorstelling.link]))
    event.add('organizer', 'doelen@doelenics.nl')
    event.add('location', voorstelling.room)
    # At creation sequence must be 0, when updating this must be incremented.
    event.add('sequence', voorstelling.sequence)
    return event

def event2voorstelling(event):
    """
        Convert a :class:`icalendar.Event` instance to an internal
        :class:`dedoelen.core.models.Voorstelling` instance.

        :param event: event in the calendar
        :type event: :class:`icalender.Event` 
        :returns: event in De Doelen
        :rtype: :class:`dedoelen.core.models.Voorstelling`
    """
    voorstelling = Voorstelling()
    voorstelling.title = str(event['summary'])
    voorstelling.tstart = event['dtstart'].dt
    voorstelling.tend = event['dtend'].dt
    voorstelling.room = str(event['location'])
    desc = event['description'].to_ical()
    voorstelling.link = desc.split('\n')[-1].split('\\n')[-1]
    if '\\n' in desc:
        voorstelling.description = '\n'.join(desc.split('\\n')[:-1])
    else:
        voorstelling.description = '\n'.join(desc.split('\n')[:-1])
    voorstelling.description = voorstelling.description.replace('\\n','\n')
    voorstelling.description = voorstelling.description.replace('\\,',',')
    voorstelling.description = voorstelling.description.replace('\\;',';')
    voorstelling.sequence = int(event['sequence'])
    return voorstelling
