
import datetime
import icalendar
import logging

from dedoelen.core import convert
from dedoelen.core.conf import settings

logger = logging.getLogger(__name__)

def update_voorstellingen(voorstellingen):
    """
        Update events in the calendar file. This update is based on a newly
        collected set of events, and previous events read from the calendar. Old
        events are those that are in the past. These events are in the event
        list from the previous calendar file, but not necessarily in the list of
        new events. Updated events are in the list of new events, and their link
        is in the list of previous events (link is assumed constant). New events
        are those which link is not in the list of previous links. Deleted
        events are those that are in the list of events from the previous
        calendar file, but are not in the new list and are not updated or old.

        :param voorstellingen: :class:`dedoelen.core.models.Voorstelling`\
                instances that are newly retrieved.
        :type voorstellingen: list
        :returns: updated list of :class:`dedoelen.core.models.Voorstelling`\
                instances
        :rtype: list
    """
    # read the previous events from the calendar
    with open(settings.OUTFILE, "rb") as fid:
        previous_cal = icalendar.Calendar.from_ical(fid.read())
    prev_v = [convert.event2voorstelling(x) for x in
            previous_cal.walk("VEVENT")]
    logger.info("Loaded %i previous events." % len(prev_v))

    old_v = [x for x in prev_v if x.tstart.date() < datetime.now()]
    logger.info("Found %i past events." % len(old_v))
    # previously unseen links are new by definition
    prev_links = [x.link for x in prev_v]
    nieuw_toegevoegd = [x for x in voorstellingen if x.link not in prev_links]
    logger.info("Found %i new events." % len(nieuw_toegevoegd))

    # updated events are those where the links are already known but the
    # voorstelling instances are not the same.
    updated_v = [x for x in voorstellingen if x.link in prev_links and x not in
            prev_v]
    logger.info("Found %i updated events." % len(updated_v))

    # deleted events are those that are in the previous list of events, but not
    # in the new list of events and not in the updated list of events. They are
    # also not in the list of old events (past events).
    deleted_v = [x for x in prev_v if x not in voorstellingen and x not in
            updated_v and x not in old_v]
    logger.info("Found %i deleted events." % len(deleted_v))

    all_v = []
    # add all new events
    all_v.extend(nieuw_toegevoegd)
    # add all past events
    all_v.extend(old_v)
    # add all events that are unchanged previous events.
    all_v.extend([x for x in prev_v if x not in updated_v and x not in
        deleted_v and x not in old_v])
    # update the sequence number for all updated events and add those.
    for v in updated_v:
        logger.info("Updated event: %s. Sequence is now: %i" % (v.title,
            v.sequence+1))
        v.sequence += 1
    all_v.extend(updated_v)

    return all_v
