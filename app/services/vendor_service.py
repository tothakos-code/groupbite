import json
import logging
from uuid import uuid4
from sqlalchemy import select
from app.entities import session
from app.entities.vendor import Vendor, VendorType


class VendorService:
    def find_all_active():
        result = []
        for a in Vendor.find_all_active():
            result.append(a.serialized)
        return json.dumps(result)
