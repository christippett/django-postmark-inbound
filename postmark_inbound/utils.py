from functools import wraps


class ChainableBase(object):
    def _generate(self):
        s = self.__class__.__new__(self.__class__)
        s.__dict__ = self.__dict__.copy()
        return s


def chain(func):
    @wraps(func)
    def decorator(self, *args, **kw):
        self = self._generate()
        func(self, *args, **kw)
        return self
    return decorator


class InboundMailRelationMapper(ChainableBase):
    """
    Creates a model instance for each data item. Keyword arguments are
    appended to each item in the data.
    """
    def __init__(self, **kwargs):
        # Common attributes applicable to all models are passed as keyword argments (e.g. model instance for a shared foreign key)
        self.common_attributes = kwargs

    @chain
    def data(self, data):
        self.data = data
        # Append arguments from class initiation to each item in the data
        self.append(self.common_attributes)

    @chain
    def append(self, dict_data):
        # If there are multiple relations, loop through and append `dict_data` to each child object. If the key already exists in the data, it will be overwritten
        if isinstance(self.data, list):
            for data in self.data:
                for key, value in dict_data.items():
                    data[key] = value

        # Single relation, no loop required
        elif isinstance(self.data, dict):
            for key, value in dict_data.items():
                self.data[key] = value

    @chain
    def create_for(self, target_model):
        # Multiple relation
        if isinstance(self.data, list):
            relations = []
            for data in self.data:
                relations.append(target_model.objects.create(**data))
            return relations

        # Single relation
        elif isinstance(self.data, dict):
            return target_model.objects.create(**self.data)
