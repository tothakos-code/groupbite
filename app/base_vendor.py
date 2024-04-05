
class BaseVendor(object):
    def __init__(self, name, id=-1, configuration={}, settings={}):
        self.name = name
        self.id = id
        self.configuration = configuration
        self.settings = settings

    def scan(self):
        raise NotImplementedError("Subclasses must implement the scan method")

    def test(self):
        raise NotImplementedError("Subclasses must implement the test method")

    def get(self):
        raise NotImplementedError("Subclasses must implement the get method")
