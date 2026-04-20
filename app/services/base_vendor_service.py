class BaseVendorService:
    def __init__(self, vendor_id):
        self.vendor_id = vendor_id

    @classmethod
    def register(cls):
        pass

    def scan(self, db, menu_date):
        raise NotImplementedError("This vendor requires manual menu entry")
