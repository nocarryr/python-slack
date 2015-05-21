from abc import ABCMeta
from collections import Sequence

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
    
class SlackObjectContainer(SlackObject):
    __metaclass__ = ABCMeta
    container_attribute = None
    child_class = None
    def __init__(self, **kwargs):
        self._children = self._container_type()
        super(SlackObjectContainer, self).__init__(**kwargs)
    def add_child(self, child_data=None, **kwargs):
        if child_data is not None:
            kwargs.update(child_data)
        kwargs.setdefault('parent', self)
        cls = self.child_class
        return cls(**kwargs)
    def __iter__(self): return self._children.__iter__()
    def __len__(self): return self._children.__len__()
    def __getitem__(self, key): return self._children.__getitem__(key)
    def __setitem__(self, key, item): self._children.__setitem__(key, item)
    def __contains__(self, item): return self._children.__contains__(item)
    def __repr__(self): return repr(self._children)
    __hash__ = None
    
class SlackObjectDict(SlackObjectContainer):
    child_id_attribute = 'id'
    _container_type = dict
    def __init__(self, **kwargs):
        super(SlackObjectDict, self).__init__(**kwargs)
        attr = self.container_attribute
        if attr is not None:
            items = kwargs.get(attr, {})
            if isinstance(items, dict):
                item_iter = items.items()
            elif isinstance(items, Sequence) or isinstance(items, set):
                item_iter = ((None, item) for item in items)
            else:
                item_iter = None
            if item_iter is not None:
                for key, child_data in item_iter:
                    self.add_child(key, child_data)
    def add_child(self, key=None, child_data=None, **kwargs):
        obj = super(SlackObjectDict, self).add_child(child_data, **kwargs)
        if key is None:
            key = getattr(obj, self.child_id_attribute)
        self[key] = obj
        return obj
    def get(self, key, default=None):
        return self._children.get(key, default)
    def __delitem__(self, key): del self._children[key]
    def clear(self): self._children.clear()
    def items(self): return self._children.items()
    def keys(self): return self._children.keys()
    def values(self): return self._children.values()
    def update(self, other_dict=None, **kwargs):
        if other_dict is not None:
            for k, v in other_dict.items():
                self[k] = v
        if len(kwargs):
            for k, v in kwargs.items():
                self[k] = v

SlackObjectDict.register(dict)

class SlackObjectList(SlackObjectContainer):
    _container_type = list
    def __init__(self, **kwargs):
        super(SlackObjectList, self).__init__(**kwargs)
        attr = self.container_attribute
        if attr is not None:
            for child_data in kwargs.get(attr, []):
                self.add_child(**child_data)
    def add_child(self, child_data=None, **kwargs):
        obj = super(SlackObjectList, self).add_child(child_data, **kwargs)
        self.append(obj)
        return obj
    def append(self, item): self._children.append(item)
    def remove(self, item): self._children.remove(item)
    def index(self, item, *args): return self._children.index(item, *args)
    
SlackObjectList.register(list)
    
