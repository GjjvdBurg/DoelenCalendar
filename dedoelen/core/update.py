
import icalendar
import logging

from dedoelen.core import convert
from dedoelen.core.conf import settings

logger = logging.getLogger(__name__)

def update_voorstellingen(voorstellingen):
    """
    """
    # read the previous events from the calendar
    with open(settings.OUTFILE, "rb") as fid:
        previous_cal = icalendar.Calendar.from_ical(fid.read())
    prev_v = [convert.event2voorstelling(x) for x in
            previous_cal.walk("VEVENT")]
    logger.info("Loaded %i previous events." % len(prev_v))

    for pv, v in zip(sorted(prev_v), sorted(voorstellingen)):
        print '='*50
        print '%s || %s' % (pv.title, v.title)
        print 'Title:', pv.title == v.title
        print 'Link:', pv.link == v.link
        print 'StartT: %s || %s (%s)' % (pv.tstart, v.tstart, str(pv.tstart ==
            v.tstart))
        print 'EndT:', pv.tend == v.tend
        print 'Room:', pv.room == v.room
        print 'Desc:', pv.description == v.description
        print 'Hash: %i || %i (%s)' % (hash(pv), hash(v), str(hash(pv) ==
            hash(v)))
        if pv.description != v.description:
            print pv.description
            print '%%' * 10
            print v.description

    prev_links = [x.link for x in prev_v]
    # previously unseen links are new by definition
    nieuw_toegevoegd = [x for x in voorstellingen if x.link not in prev_links]
    logger.info("Found %i new events." % len(nieuw_toegevoegd))

    # updated events are those where the links are already known but the
    # voorstelling instances are not the same.
    updated_v = [x for x in voorstellingen if x.link in prev_links and x not in
            prev_v]
    logger.info("Found %i updated events." % len(updated_v))

    # deleted events are those that are past events (the RSS feed removes these)
    # and events that are in the list of previous events, but are not in the
    # list of current events and are not updated.
    deleted_v = [x for x in prev_v if x not in voorstellingen and x not in
            updated_v]
    logger.info("Found %i deleted events." % len(deleted_v))

    all_v = []
    # add all new events
    all_v.extend(nieuw_toegevoegd)
    # add all events that are unchanged previous events.
    all_v.extend([x for x in prev_v if x not in updated_v and x not in
        deleted_v])
    # update the sequence number for all updated events and add those.
    for v in updated_v:
        v.sequence += 1
    all_v.extend(updated_v)

    return all_v
