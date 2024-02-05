import json
import logging
from uuid import uuid4
from sqlalchemy import select
from app.entities import session
from app.entities.vendor import Vendor, VendorType


class VendorService:
    def add_vendor(vendor_p):
        db_vendor = session.query(Vendor).filter_by(name = vendor_p.name).first()

        if not db_vendor:
            # insert
            session.add(Vendor(id=uuid4(),name=vendor_p.name))
            logging.info("Vendor registered: {0}".format(vendor_p.name))
        else:
            vendor_p.id = db_vendor.id

        session.commit()
        session.close()

    def get_vendors():
        session = Session()
        db_vendors = session.query(Vendor).all()
        session.close()

        result = {}
        if not db_vendors:
            return result

        for vendor in db_vendors:
            result[vendor.id] = vendor.serialized

        return result

    def get_one_vendor(vendor_id):
        session = Session()
        db_vendor = session.query(Vendor).filter(Vendor.id == vendor_id).all()
        session.close()

        return db_vendor
