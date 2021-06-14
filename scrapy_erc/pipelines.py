# -*- coding: utf-8 -*-
# Don't forget to add pipelines to the ITEM_PIPELINES setting

from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from scrapy_erc.models import PCDWaste_Listing, PCDWaste_LocalGov, db_connect, create_table
from scrapy_erc.items import PCDWaste_Listing_Item, PCDWaste_LocalGov_Item
import logging

from dateparser import parse
from dateutil.relativedelta import relativedelta
import calendar
import pandas as pd
import re

class ScrapyErcPipeline(object):

    # https://stackoverflow.com/questions/32743469/scrapy-python-multiple-item-classes-in-one-pipeline
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        logging.info("**** Pipeline Database Connected ****")

    def process_item(self, item, spider):
        if isinstance(item, PCDWaste_Listing_Item):
            return self.PCDWaste_Listing_Pipeline(item, spider)
        if isinstance(item, PCDWaste_LocalGov_Item):
            return self.PCDWaste_LocalGov_Pipeline(item, spider)

    def PCDWaste_Listing_Pipeline(self, item, spider):
        session = self.Session()

        for field in item.fields:
            item.setdefault(field, 'NULL')

        # item.setdefault('area_rai', None)
        item.setdefault('tons_daily', None)

        # # filter duplicates
        # exist_listing = session.query(PCDWaste_Listing).filter_by(order = item["order"]).first()
        # if exist_listing is not None:  # the current listing exists
        #     message_profile_dropped = "Duplicate item found for %s" % item["order"]
        #     raise DropItem(message_profile_dropped)
        #     session.close()
        #
        # else:
        pcdwaste_listing = PCDWaste_Listing()
        pcdwaste_listing.order = item["order"]
        pcdwaste_listing.operator_th = item["operator_th"]
        pcdwaste_listing.operator_href = item["operator_href"]
        pcdwaste_listing.operator_no = item["operator_href"].split("=")[1]
        pcdwaste_listing.location_name_th = item["location_name_th"]
        pcdwaste_listing.location_href = item["location_href"]
        pcdwaste_listing.location_no = item["location_href"].split("=")[1]
        pcdwaste_listing.fulladdress_th = item["fulladdress_th"]
        pcdwaste_listing.address_th = item["address_th"]
        pcdwaste_listing.subdistrict_th = item["subdistrict_th"]
        pcdwaste_listing.district_th = item["district_th"]
        pcdwaste_listing.province_th = item["province_th"].replace('\d+', '') # remove numbers/postcodes from string
        # pcdwaste_listing.subdistrict_th_district_th_province_th = (item["subdistrict_th"] + "~" + item["district_th"] + "~" + item["province_th"].replace('\d+', ''))
        pcdwaste_listing.postcode = item["postcode"]
        pcdwaste_listing.area_rai = item["area_rai"]
        pcdwaste_listing.type_th = item["type_th"]
        pcdwaste_listing.compliance_th = item["compliance_th"]
        pcdwaste_listing.tons_daily = item["tons_daily"]
        pcdwaste_listing.lastupdate = item["lastupdate"]

        # # check whether the listing exists and load item
        # exist_listing = session.query(PCDWaste_Listing).filter_by(location_href = pcdwaste_listing.location_href).first()
        # if exist_listing is not None:  # the current listing exists
        #     pcdwaste_listing.location_href = exist_listing
        #     return None
        # else:
        pcdwaste_listing.location_href = pcdwaste_listing.location_href
        try:
            session.add(pcdwaste_listing)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item

    def PCDWaste_LocalGov_Pipeline(self, item, spider):
        session = self.Session()

        for field in item.fields:
            item.setdefault(field, 'NULL')

        # item.setdefault('area_rai', None)
        # item.setdefault('tons_daily', None)

        # # filter duplicates
        # exist_listing = session.query(PCDWaste_Listing).filter_by(operator_no = item["operator_no"]).first()
        # if exist_listing is not None:  # the current listing exists
        #     message_profile_dropped = "Duplicate item found for %s" % item["operator_no"]
        #     raise DropItem(message_profile_dropped)
        #     session.close()
        #
        # else:
        pcdwaste_localgov = PCDWaste_LocalGov()
        pcdwaste_localgov.operator_no = item["operator_href"].split("=")[1]
        pcdwaste_localgov.local_entity_th = item['local_entity_th'].replace("ข้อมูลองค์กรปกครองส่วนท้องถิ่น ","")
        pcdwaste_localgov.fulladdress_th = item['fulladdress_th'].replace(" ถนน - ต"," ต").replace("- หมู่ - ","").replace('- หมู่ ', 'หมู่ ').replace("0 หมู่ ","หมู่ ") # replace "- " and "0 " before "Moo" at beginning of string
        pcdwaste_localgov.address_th = re.sub('\ -$', '', item["address_th"].replace(" ถนน - ต"," ต")).replace("- หมู่ - ","").replace('- หมู่ ', 'หมู่ ').replace("0 หมู่ ","หมู่ ") # replace "- " and "0 " before "Moo" at beginning of string
        pcdwaste_localgov.subdistrict_th = item["subdistrict_th"]
        pcdwaste_localgov.district_th = item["district_th"]
        pcdwaste_localgov.province_th = item["province_th"]
        pcdwaste_localgov.postcode = item["postcode"]
        pcdwaste_localgov.phone = item['phone']
        pcdwaste_localgov.geolocation = item['geolocation'].replace("x : ","").replace(" y : ",", ").replace("0, 0","")
        pcdwaste_localgov.administrative_area_th = item['administrative_area_th']
        pcdwaste_localgov.operator_href = item['operator_href']
        pcdwaste_localgov.lastupdate = item["lastupdate"]

        # # check whether the listing exists and load item
        # exist_listing = session.query(PCDWaste_Listing).filter_by(operator_no = pcdwaste_localgov.operator_no).first()
        # if exist_listing is not None:  # the current listing exists
        #     pcdwaste_localgov.operator_no = exist_listing
        #     return None
        # else:
        pcdwaste_localgov.operator_no = pcdwaste_localgov.operator_no
        try:
            session.add(pcdwaste_localgov)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
