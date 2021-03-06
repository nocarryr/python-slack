from python_slack.slackobjects.base import SlackObject, SlackObjectDict

class Profile(SlackObject):
    _attributes = {
        'first_name':{'py_type':unicode}, 
        'last_name':{'py_type':unicode}, 
        'real_name':{'py_type':unicode}, 
        'email':{'py_type':unicode}, 
        'skype':{'py_type':unicode}, 
        'phone':{'py_type':unicode}, 
        'image_24':{'py_type':unicode}, 
        'image_32':{'py_type':unicode}, 
        'image_48':{'py_type':unicode}, 
        'image_72':{'py_type':unicode}, 
        'image_192':{'py_type':unicode}, 
    }
class User(SlackObject):
    _attributes = {
        'name':{'py_type':unicode}, 
        'deleted':{'py_type':bool}, 
        'is_admin':{'py_type':bool}, 
        'is_owner':{'py_type':bool}, 
        'is_primary_owner':{'py_type':bool}, 
        'is_restricted':{'py_type':bool}, 
        'is_ultra_restricted':{'py_type':bool}, 
        'has_2fa':{'py_type':bool}, 
        'has_files':{'py_type':bool}, 
    }
    _child_classes = {'profile':Profile}
    
class Users(SlackObjectDict):
    container_attribute = 'users'
    child_class = User
    def get_users(self):
        data = self.call_api('users.list')
        if data is None:
            return
        for user_data in data['members']:
            if user_data['id'] in self:
                ## TODO: see channel.ChannelContainerBase
                pass
            else:
                self.add_child(**user_data)
    
