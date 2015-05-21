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
    @classmethod
    def api_method_name(cls, method):
        return '.'.join([cls.api_method_prefix, method])
    def get_messages(self, **kwargs):
        kwargs.setdefault('count', 100)
        kwargs['channel'] = self.id
        method = self.api_method_name('history')
        data = self.call_api(method, **kwargs)
        if data is None:
            return
        for msg_data in data['messages']:
            self.messages.add_child(**msg_data)
        if not data.get('has_more'):
            return
        ## TODO: iterate and get the rest of the messages
        
        
class Channel(ChannelBase):
    api_method_prefix = 'channels'
    
class Group(ChannelBase):
    api_method_prefix = 'groups'
    
class ChannelContainerBase(SlackObjectDict):
    def get_channels(self):
        method = self.child_class.api_method_name('list')
        data = self.call_api(method)
        if data is None:
            return
        for chan_data in data['channels']:
            if chan_data['id'] in self:
                ## TODO: update the object. build update methods in SlackObject
                pass
            else:
                self.add_child(**chan_data)
        
class Channels(ChannelContainerBase):
    container_attribute = 'channels'
    child_class = Channel
    
    
class Groups(ChannelContainerBase):
    container_attribute = 'groups'
    child_class = Group
