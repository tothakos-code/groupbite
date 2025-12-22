import logging

from app.entities.vendor import VendorType, Vendor
from app.repositories.vendor_repository import VendorRepository
from app.services.base_vendor_service import BaseVendorService


class VendorServiceFactory:

    _vendor_services = {}

    @classmethod
    def register_vendor_service(cls, vendor: Vendor, service_class: BaseVendorService):
        cls._vendor_services[vendor.id] = service_class

    @classmethod
    def get_service(cls, db, vendor_id: str) -> BaseVendorService:
        vendor = VendorRepository(db).get_by_id(vendor_id)
        if not vendor:
            raise ValueError(f"Vendor {vendor_id} not found")
        logging.info(cls._vendor_services)
        logging.info(vendor.id)
        if vendor.id in cls._vendor_services:
            service_class = cls._vendor_services[vendor.id]
        else:
            service_class = BaseVendorService

        return service_class(vendor_id)
