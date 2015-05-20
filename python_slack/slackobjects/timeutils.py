import datetime
import numbers
try:
    import pytz
    UTC = pytz.UTC
except ImportError:
    UTC = None
    
from python_slack.slackobjects.base import AttributeValue

    
def make_dt_aware(dt):
    if UTC is not None:
        if dt.tzinfo is not None:
            dt = UTC.normalize(dt)
        else:
            dt = UTC.localize(dt)
    return dt
    
EPOCH = make_dt_aware(datetime.datetime(1970, 1, 1))

class Timestamp(AttributeValue):
    def get_value(self):
        return getattr(self, 'value_dt', None)
    def set_value(self, value):
        if value is None:
            self.value = value
            return
        if isinstance(value, basestring):
            value = float(value)
        if isinstance(value, numbers.Number):
            ts = value
            dt = make_dt_aware(datetime.datetime.utcfromtimestamp(value))
        elif isinstance(value, datetime.datetime):
            dt = make_dt_aware(value)
            td = dt - EPOCH
            ts = td.total_seconds()
        self.value_dt = dt
        self.value_ts = ts
        
