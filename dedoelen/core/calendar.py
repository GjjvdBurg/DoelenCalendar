
import icalendar

from datetime import datetime, timedelta

from dedoelen.core import convert

def make_calendar(voorstellingen):
    """
    """
    cal = icalendar.Calendar()
    cal.add('prodid', '-// Calendar for events in De Doelen//NL')
    cal.add('version', '2.0')
    cal.add('x-wr-timezone', u"Europe/Amsterdam")

    tzc = icalendar.Timezone()
    tzc.add('tzid', 'Europe/Amsterdam')
    tzc.add('x-lic-location', 'Europe/Amsterdam')

    tzs = icalendar.TimezoneStandard()
    tzs.add('tzname', 'CET')
    tzs.add('dtstart', datetime(1970, 10, 25, 3, 0, 0))
    tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
    tzs.add('TZOFFSETFROM', timedelta(hours=2))
    tzs.add('TZOFFSETTO', timedelta(hours=1))

    tzd = icalendar.TimezoneDaylight()
    tzd.add('tzname', 'CEST')
    tzd.add('dtstart', datetime(1970, 3, 29, 2, 0, 0))
    tzd.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
    tzd.add('TZOFFSETFROM', timedelta(hours=1))
    tzd.add('TZOFFSETTO', timedelta(hours=2))

    tzc.add_component(tzs)
    tzc.add_component(tzd)
    cal.add_component(tzc)

    cal.add('method', 'REQUEST')

    for voorstelling in voorstellingen:
        cal.add_component(convert.voorstelling2event(voorstelling))
    return cal
