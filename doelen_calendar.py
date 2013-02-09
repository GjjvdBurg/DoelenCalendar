#!/usr/bin/python

import feedparser
import pytz
import icalendar
import mechanize
import cookielib
import time
import locale
import os
import logging
import unicodedata

from datetime import datetime, timedelta
from functools import total_ordering
from urllib2 import URLError
from html2text import html2text
from bs4 import BeautifulSoup

# GLOBAL variables
OUTDIR = '/home/gertjan/Dropbox/Public/doelen'
AMSTERDAM = pytz.timezone('Europe/Amsterdam')

if os.name == 'posix':
    locale.setlocale(locale.LC_ALL, 'nl_NL.utf8')
else:
    locale.setlocale(locale.LC_ALL, 'nld_nld')

logger = logging.getLogger("doelen_logger")
logger.setLevel(logging.WARNING)

@total_ordering
class Voorstelling:
    def __init__(self, titel="", link="", startT=None, eindT=None,
                 zaal="", omschrijving=""):
        self.titel = titel
        self.link = link
        self.startT = startT
        self.eindT = eindT
        self.zaal = zaal
        self.omschrijving = omschrijving

    def __str__(self):
        string = ""
        string += self.titel
        string += "Start: " + self.startT.strftime("%A %d %m %Y %H:%M")
        string += "Eind: " + self.eindT.strftime("%A %d %m %Y %H:%M")
        string += "Zaal: " + self.zaal
        return string

    def __lt__(self, other):
        if not self.startT == other.startT:
            return self.startT < other.startT
        else:
            return self.eindT < other.eindT

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def maak_voorstellingen(alle_links):
    br = mechanize.Browser()
    #cj = cookielib.FileCookieJar("cookies")
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(True)

    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    br.add_headers = [('User-agent', 'Mozilla/5.0 (X11; U; Linux x86_64;\
                       rv:18.0) Gecko/20100101 Firefox/18.0')]

    voorstellingen = []
    for link in alle_links:
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
            voorstellingen.append(voorstelling)
        time.sleep(3)

    return voorstellingen


def maak_voorstelling(html, link):
    #soup = BeautifulSoup(html)
    # Implemented because some pages return with <> replaced with &lt,&gt
    soup = BeautifulSoup(html, "html.parser")

    if 'Concert niet gevonden' in html:
        return None

    v = Voorstelling()
    v.link = link

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

    print v.titel
    datum = soup.find("dt", text="Datum").parent.findNext("dd").contents[0]
    try:
        date = datetime.strptime(datum, "%A %d %b %Y").date()
    except:
        print "Ongeldige datum %s voor voorstelling %s" % (datum, v.titel)
        #logger.warning("Ongeldige datum %s voor voorstelling %s" %

    aanvang_tag = soup.find("dt", text="Aanvang")
    if aanvang_tag:
        starttijd = aanvang_tag.findNextSiblings("dd")[0].contents[0]
        try:
            sTijd = datetime.strptime(starttijd, "%H:%M uur").time()
            v.startT = datetime.combine(date, sTijd)
            v.startT.tzinfo = AMSTERDAM
        except:
            print "Ongeldige aanvangstijd %s voor voorstelling %s" % (starttijd,
                                                                      v.titel)

    eind_tag = soup.find("dt", text="Eind")
    if eind_tag:
        eindtijd = eind_tag.findNextSiblings("dd")[0].contents[0]
        try:
            eTijd = datetime.strptime(eindtijd, "%H:%M uur").time()
            if eTijd < sTijd:
                v.eindT = datetime.combine(date + timedelta(hours=24), eTijd)
            else:
                v.eindT = datetime.combined(date, eTijd)
        except:
            print "Ongeldige eindtijd %s voor voorstelling %s" % (eindtijd, 
                                                                  v.titel)
    else:
        v.eindT = v.startT + timedelta(hours=3)
    v.eindT.tzinfo = AMSTERDAM

    zaal_tag = soup.find("dt", text="Zaal")
    if zaal_tag:
        v.zaal = zaal_tag.findNextSiblings("dd")[0].contents[0]

    perf_tag = soup.find(id='performers')
    desc_tag = soup.find(id='description')
    if perf_tag:
        perf = html2text(perf_tag.encode('ascii'))
    else:
        print 'No performers at: ', link
        perf = ''
    if desc_tag:
        desc = html2text(desc_tag.encode('ascii'))
    else:
        print 'No description at: ', link
        desc = ''

    v.omschrijving = '\n'.join([perf, desc])

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

    tzd = icalendar.TimeZoneDaylight()
    tzd.add('tzname', 'CEST')
    tzd.add('dtstart', datetime(1970, 3, 29, 2, 0, 0))
    tzd.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
    tzd.add('TZOFFSETFROM', timedelta(hours=1))
    tzd.add('TZOFFSSETTO', timedelta(hours=2))

    tzc.add_component(tzs)
    tzc.add_component(tzd)
    kal.add_component(tzc)

    for voorstelling in alle_voorstellingen:
        event = icalendar.Event()
        event.add('summary', voorstelling.titel)


def main():
    FEED_URL = 'http://www.dedoelen.nl/_rss/rss.php?type=voorstellingen'
    print 'Feed ophalen...'
    feed = feedparser.parse(FEED_URL)

    print "Links verzamelen..."
    links = []
    for entry in feed.entries:
        links.append(entry.link)

    print 'Aantal links gevonden: %d' % len(links)

    print 'Voorstellingen ophalen...'
    voorstellingen = maak_voorstellingen(links)

    cal = maak_icalendar(voorstellingen)
    f = open(OUTDIR + os.sep + datetime.datetime.now().strftime('%Y%m%d') +
    '_doelen.ics', 'wb')
    f.write(cal.to_ical())
    f.close()



if __name__=='__main__':
    main()
