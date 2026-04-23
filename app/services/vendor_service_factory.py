from app.plugin_registry import PluginRegistry
from app.repositories.vendor_repository import VendorRepository
from app.services.base_vendor_service import BaseVendorService


class VendorServiceFactory:

    @classmethod
    def get_service(cls, db, vendor_id: str) -> BaseVendorService:
        vendor = VendorRepository(db).get_by_id(vendor_id)
        if not vendor:
            raise ValueError(f"Vendor {vendor_id} not found")
        if vendor.plugin_id:
            service_class = PluginRegistry.get(vendor.plugin_id) or BaseVendorService
        else:
            service_class = BaseVendorService
        return service_class(vendor_id)
