from unidecode import unidecode

class BaseVendor(object):
    def __init__(self, name, config):
        self.id = -1
        self.name = name
        self.code_name = unidecode(name)
        self.config = config

    def scan(self):
        raise NotImplementedError("Subclasses must implement the scan method")

    def test(self):
        raise NotImplementedError("Subclasses must implement the scan method")

    def get(self):
        raise NotImplementedError("Subclasses must implement the scan method")
