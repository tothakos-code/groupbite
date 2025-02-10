from typing import Any, Callable
import json
import logging
from app.entities.vendor import Vendor, VendorType
from app.services.vendor_service import VendorService
from app.base_vendor import BaseVendor
from datetime import date

class VendorFactory:
    _vendors = {}

    @classmethod
    def register(self, vendor_obj) -> None:
        """Register a new vendor."""
        Vendor.add_vendor(vendor_obj)
        self._vendors[vendor_obj.id] = vendor_obj
        return vendor_obj

    @classmethod
    def unregister(self, vendor_name) -> None:
        """Unregister a vendor."""
        # TODO: Check if vendor is deactivated first. or deactivate it.
        self._vendors.pop(vendor_name, None)

    @classmethod
    def load(self) -> None:
        """Load basic vendors from db"""
        vendor_dbs = Vendor.find_all_by_type(VendorType.BASIC)

        for vendor_db in vendor_dbs:
            vendor_obj = BaseVendor(
                name=vendor_db.name,
                id=str(vendor_db.id),
                configuration={},
                settings=vendor_db.settings
                )

            self._vendors[vendor_obj.id] = vendor_obj
            vendor_db._validate_settings()
            # scheduling jobs
            if vendor_db.settings["closure_scheduler_active"]["value"]:
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.settings["closure_scheduler"]["value"].split(":")
                schedule_task(str(vendor_db.id) + "-closure", int(hh), int(mm), vendor_db.closure_wrapper)

            if vendor_db.settings["closed_scheduler_active"]["value"]:
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.settings["closed_scheduler"]["value"].split(":")
                schedule_task(str(vendor_db.id) + "-closed", int(hh), int(mm), vendor_db.closed_wrapper)

            if vendor_db.settings["auto_email_order"]["value"]:
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.settings["email_order_scheduler"]["value"].split(":")
                schedule_task(str(vendor_db.id) + "-email-order", int(hh), int(mm), vendor_db.email_ordering_wrapper)


    @classmethod
    def get_vendors(self) -> str:
        return json.dumps(VendorService.get_vendors());

    @classmethod
    def get_vendor_objects(self) -> dict:
        return self._vendors;

    @classmethod
    def get_one_vendor_object(self, vendor_id):
        if vendor_id in self._vendors:
            return self._vendors[vendor_id]
        return None
