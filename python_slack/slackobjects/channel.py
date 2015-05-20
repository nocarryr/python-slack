from python_slack.slackobjects.base import SlackObject
from python_slack.slackobjects.timeutils import Timestamp

class Member(SlackObject):
    pass
    
class Members(SlackObject):
    def __init__(self, **kwargs):
        self.members = {}
        for member_id in kwargs.get('members', []):
            self.members[member_id] = Member(id=member_id, parent=self)
            
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
    _child_classes = {'members':Members, 'topic':Topic, 'purpose':Purpose}
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
