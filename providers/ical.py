from datetime import datetime
from dateutil.relativedelta import relativedelta
from icalevents.icalevents import events
from collections import namedtuple


EventData = namedtuple('EventData', ['summary', 'start'])


def get_event(event):
    return EventData(summary=event.summary, start=event.start)


class ICal:
    def __init__(self, url):
        self.url = url
        self.events = None


    def get(self):
        if self.events is None or self.should_update():
            end = datetime.today() + relativedelta(months=1)
            self.events = [get_event(e) for e in events(self.url, end=end)]
        return self.events


    def should_update(self):
        return True
