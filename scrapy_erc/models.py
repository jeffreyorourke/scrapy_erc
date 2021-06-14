# -*- coding: utf-8 -*-

dbschema = 'erc'

import os
from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Date, DateTime, Float, Boolean, Text
from scrapy.utils.project import get_project_settings

Base = declarative_base()

def db_connect():  # Performs database connection using database settings from settings.py and returns sqlalchemy engine instance
    return create_engine(get_project_settings().get("CONNECTION_STRING"), pool_size=10, connect_args={'options': '-csearch_path={}'.format(dbschema)})

def create_table(engine):
    Base.metadata.create_all(engine)

class PCDWaste_Listing(Base):
    __tablename__ = "pcdwaste_listing"
    id = Column(Integer, primary_key=True)

    # scraped fields
    order = Column('order', Integer)
    location_no = Column('location_no', Integer)
    location_name_th = Column('location_name_th', String(255))

    operator_no = Column('operator_no', Integer)
    operator_th = Column('operator_th', String(255))
    operator_href = Column('operator_href', String(255))

    fulladdress_th = Column('fulladdress_th', String(255))
    address_th = Column('address_th', String(255))
    subdistrict_th = Column('subdistrict_th', String(100))
    district_th = Column('district_th', String(100))
    province_th = Column('province_th', String(100))
    postcode = Column('postcode', String(10))

    area_rai = Column('area_rai', String(100))
    type_th = Column('type_th', String(100))
    compliance_th = Column('compliance_th', String(100))
    tons_daily = Column('tons_daily', Float())

    # translated fields
    operator = Column('operator', String(255))
    location_name = Column('location_name', String(255))
    fulladdress = Column('fulladdress', String(255))
    address = Column('address', String(255))
    subdistrict = Column('subdistrict', String(100))
    district = Column('district', String(100))
    province = Column('province', String(100))
    type = Column('type', String(100))
    compliance = Column('compliance', String(100))

    location_href = Column('location_href', String(255))
    lastupdate = Column('lastupdate', DateTime(timezone=True))


class PCDWaste_LocalGov(Base):
    __tablename__ = "pcdwaste_localgov"
    id = Column(Integer, primary_key=True)
    operator_no = Column('operator_no', Integer)

    local_entity_th = Column('local_entity_th', String(255)) # from scrape
    local_entity = Column('local_entity', String(255)) # Google translated from scrape
    fulladdress = Column('fulladdress', String(500)) # Google translated from scrape
    address = Column('address', String(255)) # Google translated from scrape
    subdistrict = Column('subdistrict', String(100)) # lookup scraped value from th_postalcodes_20210530 reference file
    district = Column('district', String(100)) # lookup scraped value from th_postalcodes_20210530 reference file
    province = Column('province', String(100)) # lookup scraped value from th_postalcodes_20210530 reference file
    region = Column('region', String(25)) # lookup value from th_postalcodes_20210530 reference file

    geolocation = Column('geolocation', String(255)) # from scrape
    latitude_lookup = Column('latitude_lookup', Float()) # lookup subdistrict value from th_postalcodes_20210530 reference file
    longitude_lookup = Column('longitude_lookup', Float()) # lookup subdistrict value from th_postalcodes_20210530 reference file

    # scraped fields
    fulladdress_th = Column('fulladdress_th', String(500))
    address_th = Column('address_th', String(255))
    subdistrict_th = Column('subdistrict_th', String(100))
    district_th = Column('district_th', String(100))
    province_th = Column('province_th', String(100))
    # subdistrict_th_district_th_province_th = Column('subdistrict_th_district_th_province_th', String(255))
    postcode = Column('postcode', String(20))
    phone = Column('phone', String(255))
    administrative_area_th = Column('administrative_area_th', String(255))
    administrative_area = Column('administrative_area', String(255))

    operator_href = Column('operator_href', String(255))
    lastupdate = Column('lastupdate', DateTime(timezone=True))
