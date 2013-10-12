

def voorstelling2event(voorstelling):
    """
        Converter van een :class:`dedoelen.models.Voorstelling` object naar een
        ICS calender Event.

        :param voorstelling: voorstelling in De Doelen
        :type voorstelling: :class:`dedoelen.models.Voorstelling`
        :returns: ICS event voor de voorstelling
        :rtype: :class:`icalender.Event`
    """
    event = icalendar.Event()
    event.add('summary', voorstelling.titel)
    event.add('dtstart', voorstelling.startT)
    event.add('dtend', voorstelling.eindT)
    event.add('dtstamp', datetime.now(AMSTERDAM))
    event['uid'] = str(hash(voorstelling))+'@doelenics.nl'
    event.add('last-modified', datetime.now(AMSTERDAM))
    event.add('description', '\n'.join([voorstelling.omschrijving, voorstelling.link]))
    event.add('organizer', 'doelen@doelenics.nl')
    event.add('location', voorstelling.zaal)
    # At creation sequence must be 0, when updating this must be incremented.
    event.add('sequence', voorstelling.sequence)
    return event
