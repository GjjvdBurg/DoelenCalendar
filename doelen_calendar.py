#!/usr/bin/python

import feedparser
import pytz
import icalendar
import mechanize
import cookielib
import time
import locale
import os
import sys
import unicodedata

from datetime import datetime, timedelta
from functools import total_ordering
from urllib2 import URLError
from html2text import html2text
from bs4 import BeautifulSoup

# GLOBAL variables
OUTFILE = '/home/gertjan/Dropbox/Public/doelen/doelen_kalender.ics'
AMSTERDAM = pytz.timezone('Europe/Amsterdam')
FEED_URL = 'http://www.dedoelen.nl/_rss/rss.php?type=voorstellingen'

if os.name == 'posix':
    locale.setlocale(locale.LC_ALL, 'nl_NL.utf8')
else:
    locale.setlocale(locale.LC_ALL, 'nld_nld')

@total_ordering
class Voorstelling:
    def __init__(self, titel="", link="", startT=None, eindT=None,
                 zaal="", omschrijving="", sequence=0):
        self.titel = titel
        self.link = link
        self.startT = startT
        self.eindT = eindT
        self.zaal = zaal
        self.omschrijving = omschrijving
        self.sequence = sequence

    def __str__(self):
        string = ""
        string += self.titel + "\n"
        string += self.link + "\n"
        string += "Start: " + self.startT.strftime("%A %d %m %Y %H:%M") + "\n"
        string += "Eind: " + self.eindT.strftime("%A %d %m %Y %H:%M") + "\n"
        string += "Zaal: " + self.zaal + "\n"
        string += "Omschrijving: " + self.omschrijving + "\n"
        return string

    def __lt__(self, other):
        if not self.startT == other.startT:
            return self.startT < other.startT
        else:
            return self.eindT < other.eindT

    def __eq__(self, other):
        return hash(self) == hash(other)
    def __hash__(self):
        return hash(self.link)

    def to_icsevent(self):
        event = icalendar.Event()
        event.add('summary', self.titel)
        event.add('dtstart', self.startT)
        event.add('dtend', self.eindT)
        event.add('dtstamp', datetime.now(AMSTERDAM))
        event['uid'] = str(hash(self))+'@doelenics.nl'
        event.add('last-modified', datetime.now(AMSTERDAM))
        event.add('description', '\n'.join([self.omschrijving, self.link]))
        event.add('organizer', 'doelen@doelenics.nl')
        event.add('location', self.zaal)
        # At creation sequence must be 0, when updating this must be incremented.
        event.add('sequence', self.sequence)
        return event

    def from_icsevent(self, event):
        self.titel = str(event['summary'])
        self.startT = event['dtstart'].dt
        self.eindT = event['dtend'].dt
        self.zaal = str(event['location'])
        desc = event['description'].to_ical()
        self.link = desc.split('\n')[-1].split('\\n')[-1]
        if '\\n' in desc:
            self.omschrijving = '\n'.join(desc.split('\\n')[:-1])
        else:
            self.omschrijving = '\n'.join(desc.split('\n')[:-1])
        self.sequence = int(event['sequence'])

def maak_voorstellingen(alle_links):
    br = mechanize.Browser()
    monster = cookielib.LWPCookieJar()
    br.set_cookiejar(monster)

    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(True)

    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    br.add_headers = [('User-agent', 'Mozilla/5.0 (X11; U; Linux x86_64;\
                       rv:18.0) Gecko/20100101 Firefox/18.0')]

    voorstellingen = []
    it = 0
    stopid = 0
    for link in alle_links:
        it += 1
        while True:
            try:
                response = br.open(link)
                html = response.read()
                if 'overlast van SPAM-bots' in html:
                    print 'Ze doen vervelend ...'
                    time.sleep(10)
                    continue
                break
            except URLError as e:
                print 'Er is een fout opgetreden bij het ophalen van de pagina.'
                print 'We proberen het over 5 seconden opnieuw.'
                print e.reason
                time.sleep(5)
                continue
        voorstelling = maak_voorstelling(html, link)
        if voorstelling:
            stopid = 0
            voorstellingen.append(voorstelling)
            print it, voorstelling.startT.strftime("%Y%m%d"), voorstelling.titel
            time.sleep(2)
        else:
            stopid += 1
            if stopid > 15:
                print 'De rest is niet ingevoerd, we stoppen hier.'
                break
    return voorstellingen

def maak_voorstelling(html, link):
    # Implemented because some pages return with <> replaced with &lt,&gt
    soup = BeautifulSoup(html, "html.parser")

    if 'Concert niet gevonden' in html:
        print 'Concert niet gevonden:', link
        return None

    v = Voorstelling()
    v.link = str(link)

    titel_tags = soup.find_all(attrs={'class': 'title'})
    try:
        v.titel = titel_tags[0].find_all(attrs={'class': 'main'})[0].text
        v.titel = str(v.titel)
    except IndexError:
        print '='*33 + ' IndexError ' + '='*33
        print link
        print '='*78
    except UnicodeEncodeError:
        v.titel = unicodedata.normalize('NFKD', v.titel).encode('ascii',
                                                                'ignore')

    datum = soup.find("dt", text="Datum").parent.findNext("dd").contents[0]
    try:
        date = datetime.strptime(datum, "%A %d %B %Y").date()
    except:
        print "Ongeldige datum %s voor voorstelling %s" % (datum, v.titel)
        #logger.warning("Ongeldige datum %s voor voorstelling %s" %

    aanvang_tag = soup.find("dt", text="Aanvang")
    if aanvang_tag:
        starttijd = aanvang_tag.findNextSiblings("dd")[0].contents[0]
        try:
            sTijd = datetime.strptime(starttijd, "%H.%M uur").time()
            v.startT = datetime(date.year, date.month, date.day, sTijd.hour,
                    sTijd.minute, tzinfo=AMSTERDAM)
        except:
            print "Ongeldige aanvangstijd %s voor voorstelling %s" % (starttijd,
                                                                      v.titel)

    eind_tag = soup.find("dt", text="Eind")
    if eind_tag:
        eindtijd = eind_tag.findNextSiblings("dd")[0].contents[0]
        try:
            eTijd = datetime.strptime(eindtijd, "%H.%M uur").time()
            if eTijd < sTijd:
                newdate = date + timedelta(hours=24)
                v.eindT = datetime(newdate.year, newdate.month, newdate.day,
                        eTijd.hour, eTijd.minute, tzinfo=AMSTERDAM)
            else:
                v.eindT = datetime(date.year, date.month, date.day, eTijd.hour,
                        eTijd.minute, tzinfo=AMSTERDAM)
        except ValueError:
            print "Ongeldige eindtijd %s voor voorstelling %s" % (eindtijd, 
                                                                  v.titel)
    else:
        v.eindT = v.startT + timedelta(hours=3)

    zaal_tag = soup.find("dt", text="Zaal")
    if zaal_tag:
        v.zaal = zaal_tag.findNextSiblings("dd")[0].contents[0]
        v.zaal = unicodedata.normalize('NFKD', v.zaal).encode('ascii', 'ignore')

    perf_tag = soup.find(id='performers')
    desc_tag = soup.find(id='description')
    if perf_tag:
        perf = html2text(perf_tag.encode('ascii'))
    else:
        #print 'No performers at: ', link
        perf = ''
    if desc_tag:
        desc = html2text(desc_tag.encode('ascii'))
    else:
        #print 'No description at: ', link
        desc = ''

    v.omschrijving = '\n'.join([perf, desc])
    v.omschrijving = unicodedata.normalize('NFKD', v.omschrijving).encode('ascii', 'ignore')

    return v

def maak_icalendar(alle_voorstellingen):
    """docstring for maak_icalendar"""
    kal = icalendar.Calendar()
    kal.add('prodid', '-// Kalender voor concerten in de Doelen//NL')
    kal.add('version', '2.0')
    kal.add('x-wr-timezone', u"Europe/Amsterdam")

    # Add timezone information. See
    # https://github.com/collective/icalendar/blob/master/src/icalendar/tests/test_timezoned.py
    tzc = icalendar.Timezone()
    tzc.add('tzid', 'Europe/Amsterdam')
    tzc.add('x-lic-location', 'Europe/Amsterdam')

    tzs = icalendar.TimezoneStandard()
    tzs.add('tzname','CET')
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
    kal.add_component(tzc)
    
    kal.add('method','REQUEST')
    clean_voorstellingen = [x for x in alle_voorstellingen if not x.startT is
            None]

    for voorstelling in clean_voorstellingen:
        kal.add_component(voorstelling.to_icsevent())

    return kal


def findchanges(tups):
    """docstring for findchanges"""
    def changed(x, y):
        if x.titel != y.titel:
            return False
        if x.startT != y.startT:
            return False
        if x.eindT != y.eindT:
            return False
        if x.zaal != y.zaal:
            return False
        if x.omschrijving != y.omschrijving:
            return False
        return True
    changednew = [t[1] for t in tups if changed(t[0], t[1])]
    return changednew


def update_voorstellingen(oud, nieuw):
    """
        Probeer te matchen op link, deze zijn uniek per definitie. Als een link
        de "concert niet gevonden" pagina geeft kan een voorstelling worden
        verwijderd. Tegelijkertijd kan de inhoud van een voorstelling worden
        veranderd als de link hetzelfde is. We kunnen daarom ook misschien beter
        de hash splitsen in een hash voor vergelijken tussen nieuw en oud en een
        hash voor het vergelijken van inhoud van  een voorstelling.
    """
    # we need a filter for past events, these will show up in oud but not in
    # nieuw. We also need a filter for new events. Then we need to figure out
    # which events have changed.
    firstnew = nieuw[0]
    print 'firstnew:', firstnew.startT.strftime("%Y%m%d")
    firstold = oud[0]
    print 'firstold:', firstold.startT.strftime("%Y%m%d")
    lastold = oud[-1]
    print 'lastold:', lastold.startT.strftime("%Y%m%d")
    lastnew = oud[-1]
    print 'lastnew:', lastnew.startT.strftime("%Y%m%d")
    # Completely new events, either inserted or added after the last run. These
    # events will get sequence 0
    new = set(oud) ^ set(nieuw)
    print len(oud), len(nieuw), len(new)
    # Changed events are those events not in new, but in nieuw and oud and have
    # changed properties, using the matching function: 
    potentially_changed = [x for x in nieuw if x <= lastold]
    tuples = []
    for x in oud:
        y = [p for p in potentially_changed if p == x][0]
        tuples.append((x, y))
    changednew = findchanges(tuples)
    
    return []


def update_voorstellingen(oud, links):
    """docstring for update_voorstellingen"""
    # First check if any of the old events are cancelled. If events are
    # cancelled, the link may either be removed from the list (in old but not in
    # new) or the link is in old and new, but the page returns 'Concert niet
    # gevonden'. 
    
    # Now check if any of the old events are changed. These events both have a
    # link in old and new, but the properties of the events have changed. This
    # would mean that the sequence number of the event must be incremented when
    # the changes are applied, but the UID must be kept.

    # Now add events that are new


def init():
    print "Feed ophalen ..."
    feed = feedparser.parse(FEED_URL)
    print "Links verzamelen ..."
    links = []
    for entry in feed.entries:
        links.append(entry.link)
    print "Aantal links gevonden: %d" % len(links)
    print "Voorstellingen ophalen ..."
    voorstellingen = maak_voorstellingen(links)
    print "Kalender aanmaken ..."
    cal = maak_icalendar(voorstellingen)
    with open(OUTFILE, "wb") as f:
        f.write(cal.to_ical())


def update():
    print "Feed ophalen ..."
    feed = feedparser.parse(FEED_URL)
    print "Links ophalen ..."
    links = []
    for entry in feed.entries:
        links.append(entry.link)
    del feed
    print "Aantal links gevonden: %d" % len(links)
    print "Vorige versie inlezen ..."
    cal = icalendar.Calendar.from_ical(open(OUTFILE, 'rb').read())
    oude_voorstellingen = []
    for event in cal.walk("VEVENT"):
        v = Voorstelling()
        v.from_icsevent(event)
        oude_voorstellingen.append(v)
    nieuwe_voorstellingen = update_voorstellingen(oude_voorstellingen, links)
    new_cal = maak_icalendar(nieuwe_voorstellingen)
    """
    with open(OUTFILE, "wb") as f:
        f.write(new_cal.to_ical())
    """

"""
def update():
    print "Feed ophalen ..."
    feed = feedparser.parse(FEED_URL)

    print "Links verzamelen ..."
    links = []
    for entry in feed.entries:
        links.append(entry.link)

    print "Aantal links gevonden: %d" % len(links)

    print "Voorstellingen ophalen ..."
    nieuwe_voorstellingen = maak_voorstellingen(links)

    print "Kalender inlezen ..."
    cal = icalendar.Calendar.from_ical(open(OUTFILE, 'rb').read())
    oude_voorstellingen = []
    for event in cal.walk("VEVENT"):
        v = Voorstelling()
        v.from_icsevent(event)
        oude_voorstellingen.append(v)

    geupdate_voorstellingen = update_voorstellingen(oude_voorstellingen,
            nieuwe_voorstellingen)
    new_cal = maak_icalendar(geupdate_voorstellingen)
    #with open(OUTFILE, "wb") as f:
        #f.write(new_cal.to_ical())
"""


if __name__=='__main__':
    if sys.argv[1] == 'init':
        init()
    elif sys.argv[1] == 'update':
        update()
