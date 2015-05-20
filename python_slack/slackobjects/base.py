from python_slack.utils import iterbases

class Attribute(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.py_type = kwargs.get('py_type')
        self._getter = kwargs.get('getter')
        self._setter = kwargs.get('setter')
        self.cls = kwargs.get('cls')
        self.value_cls = kwargs.get('value_cls', AttributeValue)
    @property
    def cls(self):
        return getattr(self, '_cls', None)
    @cls.setter
    def cls(self, cls):
        def find_method(name):
            for _cls in iterbases(cls):
                if not hasattr(_cls, name):
                    continue
                return getattr(_cls, name)
            return None
        if isinstance(self._getter, basestring):
            self._getter = find_method(self._getter)
        if isinstance(self._setter, basestring):
            self._setter = find_method(self._setter)
    def get_value_obj(self, instance):
        if not hasattr(instance, 'attributes'):
            instance.attributes = {}
        value = instance.attributes.get(self.name)
        if value is None:
            value = self.value_cls(attribute=self, instance=instance)
            instance.attributes[self.name] = value
        elif value.attribute is not self:
            raise Exception('%r already has attribute %s defined' % (instance, self.name))
        return value
    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self._getter is not None:
            return self._getter(instance)
        value_obj = self.get_value_obj(instance)
        return value_obj.get_value()
    def __set__(self, instance, value):
        if self._setter is not None:
            self._setter(instance, value)
        else:
            value_obj = self.get_value_obj(instance)
            value_obj.set_value(value)
        
class AttributeValue(object):
    def __init__(self, **kwargs):
        self.attribute = kwargs.get('attribute')
        self.instance = kwargs.get('instance')
        self.value = kwargs.get('value')
    def get_value(self):
        value = self.value
        py_type = self.attribute.py_type
        if value is None or py_type is None:
            return value
        if type(value) is not py_type:
            value = py_type(value)
        return value
    def set_value(self, value):
        py_type = self.attribute.py_type
        if py_type is not None and type(value) is not py_type:
            value = py_type(value)
        self.value = value
        
class SlackObject(object):
    _attributes = {'id':{'py_type':unicode}}
    def __new__(cls, **kwargs):
        attribute_names = set()
        child_classes = {}
        for subcls in iterbases(cls):
            if not issubclass(subcls, SlackObject):
                break
            if hasattr(subcls, '_attributes'):
                for key, attr_def in subcls._attributes.items():
                    attr_def.setdefault('name', key)
                    name = attr_def.get('name')
                    attribute_names.add(name)
                    if not hasattr(subcls, name):
                        attr_def.setdefault('cls', subcls)
                        attribute = Attribute(**attr_def)
                        setattr(subcls, name, attribute)
            if hasattr(subcls, '_child_classes'):
                for key, val in subcls._child_classes.items():
                    if key in child_classes:
                        continue
                    child_classes[key] = val
        obj = super(SlackObject, cls).__new__(cls)
        obj.attribute_names = attribute_names
        obj.child_classes = child_classes
        return obj
    def __init__(self, **kwargs):
        self.parent = kwargs.get('parent')
        for name in self.attribute_names:
            setattr(self, name, kwargs.get(name))
        for key in self.child_classes.keys():
            if hasattr(self, key):
                continue
            self.build_child_object(key, **kwargs.get(key, {}))
    def build_child_object(self, name, **kwargs):
        cls = self.child_classes[name]
        kwargs.setdefault('parent', self)
        obj = cls(**kwargs)
        setattr(self, name, obj)
        return obj
    
    
