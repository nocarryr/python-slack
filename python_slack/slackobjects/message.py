from python_slack.slackobjects.base import SlackObject, SlackObjectDict
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
    
class Messages(SlackObjectDict):
    container_attribute = 'messages'
    child_id_attribute = 'ts'
    child_class = Message
    
