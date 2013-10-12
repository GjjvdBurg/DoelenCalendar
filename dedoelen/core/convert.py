
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
        :class:`icalendar.Event` instance.

        :param voorstelling: event in De Doelen
        :type voorstelling: :class:`dedoelen.core.models.Voorstelling`
        :returns: ICS event for the event
        :rtype: :class:`icalender.Event`
    """
    event = icalendar.Event()
    event.add('summary', voorstelling.title)
    event.add('dtstart', voorstelling.tstart)
    event.add('dtend', voorstelling.tend)
    event.add('dtstamp', datetime.now(settings.AMSTERDAM))
    event['uid'] = str(hash(voorstelling))+'@doelenics.nl'
    event.add('last-modified', datetime.now(settings.AMSTERDAM))
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
    voorstelling.sequence = int(event['sequence'])
