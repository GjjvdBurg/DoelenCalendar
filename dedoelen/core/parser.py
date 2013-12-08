
import logging
import unicodedata

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from html2text import html2text

from dedoelen.core.models import Voorstelling
from dedoelen.core.conf import settings

logger = logging.getLogger(__name__)

def html2voorstelling(page):
    """
        Convert a scraped html page to a
        :class:`dedoelen.core.models.Voorstelling` instance. Pages that can not
        be parsed properly are ignored, and None is returned. Text entries are
        converted to ascii, and special characters are ignored. Events that have
        no start time are also ignored (None is returned).

        :param page: tuple of the page url and the page html
        :type page: tuple
        :returns: representation of the event
        :rtype: :class:`dedoelen.core.models.Voorstelling`
    """
    link, html = page
    soup = BeautifulSoup(html, "html.parser")

    if 'Concert niet gevonden' in html:
        logger.warn('Concert niet gevonden: %s' % link)
        return None

    v = Voorstelling()
    v.link = str(link)

    # get title
    title_tags = soup.find_all(attrs={'class': 'title'})
    try:
        v.title = title_tags[0].find_all(attrs={'class': 'main'})[0].text
        v.title = str(v.title)
    except IndexError:
        logger.error('IndexError for link: %s' % link)
    except UnicodeEncodeError:
        v.title = unicodedata.normalize('NFKD', v.title).encode('ascii',
                'ignore')

    # get date
    date = soup.find('dt', text="Datum").parent.findNext("dd").contents[0]
    try:
        date = datetime.strptime(date, "%A %d %B %Y").date()
    except:
        logger.error("Ongeldige datum (%s) voor voorstelling %s" % (date,
            v.title))

    # get start time
    start_tag = soup.find('dt', text='Aanvang')
    if start_tag:
        start_time = start_tag.findNextSiblings("dd")[0].contents[0]
        try:
            start_t = datetime.strptime(start_time, "%H.%M uur").time()
            t = datetime(date.year, date.month, date.day, start_t.hour,
                    start_t.minute)
            v.tstart = settings.AMSTERDAM.localize(t)
        except ValueError:
            logger.error("Ongeldige aanvangstijd (%s) voor voorstelling %s" 
                    % (start_time, v.title))
    
    # get end tag. Correct for events that end after 0:00.
    end_tag = soup.find('dt', text='Eind')
    if end_tag:
        end_time = end_tag.findNextSiblings("dd")[0].contents[0]
        try:
            end_t = datetime.strptime(end_time, "%H.%M uur").time()
            if end_t < start_t:
                newdate = date + timedelta(hours=24)
                t = datetime(newdate.year, newdate.month, newdate.day,
                        end_t.hour, end_t.minute)
                v.tend = settings.AMSTERDAM.localize(t)
            else:
                t = datetime(date.year, date.month, date.day, end_t.hour,
                        end_t.minute)
                v.tend = settings.AMSTERDAM.localize(t)
        except ValueError:
            logger.error("Ongeldige eindtijd (%s) voor voorstelling %s" 
                    % (end_time, v.title))
    else:
        v.tend = v.tstart + timedelta(hours=3)

    room_tag = soup.find("dt", text="Zaal")
    if room_tag:
        v.room = room_tag.findNextSiblings("dd")[0].contents[0]
        v.room = unicodedata.normalize('NFKD', v.room).encode('ascii', 'ignore')
    
    # performers and the event description are both convert to markdown using
    # html2text. They are then combined and converted to ascii.
    prog_tag = soup.find(id="programme")
    perf_tag = soup.find(id="performers")
    desc_tag = soup.find(id="description")
    other_tag = soup.find(id="crossVoorstellingen")
    if prog_tag:
        prog = html2text(prog_tag.encode("ascii"))
    else:
        logger.info("No programme found at link: %s" % link)
        prog = ""
    if perf_tag:
        perf = html2text(perf_tag.encode("ascii"))
    else:
        logger.info("No performers found at link: %s" % link)
        perf = ""
    if desc_tag:
        desc = html2text(desc_tag.encode("ascii").replace('\\n','\n'))
    else:
        logger.info("No description found at link: %s" % link)
        desc = ""
    if other_tag:
        other = html2text(other_tag.encode("ascii"))
    else:
        other = ""

    v.description = '\n'.join([prog, perf, desc, other])
    v.description = unicodedata.normalize('NFKD', v.description).encode('ascii',
            'ignore')

    if v.tstart is None:
        return None
    return v
