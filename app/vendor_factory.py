from typing import Any, Callable
import json

from app.entities.vendor import Vendor
from app.services.vendor_service import VendorService

class VendorFactory:
    _vendors = {}

    @classmethod
    def register(self, vendor_object) -> None:
        """Register a new vendor."""
        VendorService.add_vendor(vendor_object)
        self._vendors[vendor_object.id] = vendor_object

    @classmethod
    def unregister(self, vendor_name) -> None:
        """Unregister a vendor."""
        self._vendors.pop(vendor_name, None)

    @classmethod
    def get_vendors(self) -> str:
        return json.dumps(VendorService.get_vendors());

    @classmethod
    def get_vendor_objects(self) -> dict:
        return self._vendors;

    @classmethod
    def get_one_vendor_object(self, vendor_id):
        return self._vendors[vendor_id];
