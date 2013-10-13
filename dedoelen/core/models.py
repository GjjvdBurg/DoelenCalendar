
from functools import total_ordering

@total_ordering
class Voorstelling(object):
    """
        Een voorstelling object bevat alle informatie voor een voorstelling in
        De Doelen.

        :param title: titel van de voorstelling
        :type title: str
        :param link: www link voor het evenement
        :type link: str
        :param tstart: start tijd van het evenement
        :type tstart: :class:`datetime.time`
        :param tend: eind tijd van het evenement
        :type tend: :class:`datetime.time`
        :param room: zaal waarin het evenement plaatsvind
        :type room: str
        :param description: beschrijving van het evenement
        :type description: str
        :param sequence: sequence van het evenement (wordt gebruikt wanneer het\
                evenement wordt geupdate)
        :type sequence: int
    """
    def __init__(self, title="", link="", tstart=None, tend=None, room="",
            desc="", seq=0):
        self.title = title
        self.link = link
        self.tstart = tstart
        self.tend = tend
        self.room = room
        self.description = desc
        self.sequence = seq

    def __str__(self):
        string = (
                "%s\n"
                "%s\n"
                "Start tijd: %s\n"
                "Eind tijd: %s\n"
                "Zaal: %s\n"
                "Omschrijving: %s\n"
                % (self.title, self.link, 
                    self.tstart.strftime("%A %d %m %Y %H:%M"),
                    self.tend.strftime("%A %d %m %Y %H:%M"),
                    self.room,
                    self.description))
        return string

    def __lt__(self, other):
        if not self.tstart == other.tstart:
            return self.tstart < other.tstart
        else:
            return self.tend < other.tend
    
    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        h = hash(self.link)
        h ^= hash(self.tstart)
        h ^= hash(self.tend)
        h ^= hash(self.room)
        h ^= hash(self.description)
        return h

