from python_slack.slackobjects.base import SlackObject
from python_slack.slackobjects.timeutils import Timestamp

class MessageEdit(SlackObject):
    _attributes = {
        'user':{'py_type':unicode}, 
        'ts':{'value_cls':Timestamp}, 
    }
    
class Message(SlackObject):
    _attributes = {
        'type':{'py_type':unicode}, 
        'subtype':{'py_type':unicode}, 
        'ts':{'value_cls':Timestamp}, 
        'user':{'py_type':unicode}, 
        'text':{'py_type':unicode}, 
        'hidden':{'py_type':bool}, 
        'deleted_ts':{'value_cls':Timestamp}, 
        'event_ts':{'value_cls':Timestamp}, 
    }
    _child_classes = {'edited':MessageEdit}
    
class Messages(SlackObject):
    def __init__(self, **kwargs):
        super(Messages, self).__init__(**kwargs)
        self.messages = {}
        for msg in kwargs.get('messages', []):
            self.add_message(**msg)
    def add_message(self, **kwargs):
        kwargs.setdefault('parent', self)
        msg = Message(**kwargs)
        self.messages[msg.ts] = msg
        return msg
