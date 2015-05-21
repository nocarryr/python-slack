from python_slack.slackobjects.base import SlackObject, SlackObjectDict
from python_slack.slackobjects.timeutils import Timestamp
from python_slack.slackobjects.message import Messages

class Member(SlackObject):
    pass
    
class Members(SlackObjectDict):
    container_attribute = 'members'
    child_class = Member
    def add_child(self, key=None, child_data=None, **kwargs):
        if child_data is not None:
            if isinstance(child_data, basestring):
                child_data = {'id':child_data}
        return super(Members, self).add_child(key, child_data, **kwargs)
    
class Topic(SlackObject):
    _attributes = {
        'value':{'py_type':unicode}, 
        'creator':{'py_type':unicode}, 
        'last_set':{'value_cls':Timestamp}, 
    }
    
class Purpose(Topic):
    pass
    
class ChannelBase(SlackObject):
    _attributes = {
        'name':{'py_type':unicode}, 
        'created':{'value_cls':Timestamp}, 
        'creator':{'py_type':unicode}, 
        'is_archived':{'py_type':bool}, 
    }
    _child_classes = {
        'members':Members, 
        'topic':Topic, 
        'purpose':Purpose, 
        'messages':Messages, 
    }
    def __init__(self, **kwargs):
        members = kwargs.get('members', [])
        if isinstance(members, list):
            members = {'members':members}
            kwargs['members'] = members
        super(ChannelBase, self).__init__(**kwargs)
        
class Channel(ChannelBase):
    pass
    
class Group(ChannelBase):
    pass
