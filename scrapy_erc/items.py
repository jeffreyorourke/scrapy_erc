# -*- coding: utf-8 -*-

import scrapy
from scrapy.item import Item,Field
from itemloaders.processors import Identity,Join,MapCompose,TakeFirst
from w3lib.html import remove_tags
from w3lib.html import replace_escape_chars
from datetime import datetime,timezone
from dateutil.parser import parse
import w3lib.html
import numpy as np
import re

def rm_quotes(x):
	return x.strip(u'\u201c'u'\u201d')  # strip the unicode quotes

def rm_xa(x):
	return x.replace(u'\xa0', u' ') # remove \xa0

def rm_commas(x):
	return x.replace(',','')

def rm_whitespace(x):
	return x.strip()

def rm_dash(x):
	return x.replace("-","")

def rm_singlespace(x):
	return x.replace(" ","")

def rm_doublespace(x):
	return x.replace("  "," ")

def rm_na(x):
	return float(x if x != 'N/A' else np.nan)

def rm_forwardslash(x):
	return x.replace("/","")

def rm_bullets(x):
	return x.replace("•","")

def last13(x):
	return x[-13:]

def registration_no_withoutyear(x):
	return x[-18:-5]

def titlecase(x):
	x = x.title()
	x = x.replace("'S","'s")  # function to impose title case on string (first letter of each word uppercase, rest of words lowercase)
	return x

def datefix(x):
	if len(x) > 0:
		y = str(x)[2:-2]
		z = parse(y,fuzzy=True).replace(tzinfo=timezone.utc)
		return z
	else:
		return None

def adjust_leapyears(x):
	return x.replace("29 ก.พ.", "28 ก.พ.")  # dateparser cannot handle Thai leapy years... https://pypi.org/project/dateparser  https://github.com/scrapinghub/dateparser/pull/738

def dateparse(x):
	return dateparse(x).replace(tzinfo=timezone.utc)  # from dateutil.parser import parse

def stringtime(x):
  return datetime.strptime(x, '%d %b %Y').replace(tzinfo=timezone.utc)

def encode_thaichars(x):
	return x.replace(
	'ก','%A1',regex=True).replace('ข','%A2',regex=True).replace('ฃ','%A3',regex=True).replace('ค','%A4',regex=True).replace('ฅ','%A5',regex=True).replace('ฆ','%A6',regex=True).replace('ง','%A7',regex=True).replace('จ','%A8',regex=True).replace('ฉ','%A9',regex=True).replace('ช','%AA',regex=True).replace('ซ','%AB',regex=True).replace('ฌ','%AC',regex=True).replace('ญ','%AD',regex=True).replace('ฎ','%AE',regex=True).replace('ฏ','%AF',regex=True).replace('ฐ','%B0',regex=True).replace('ฑ','%B1',regex=True).replace('ฒ','%B2',regex=True).replace('ณ','%B3',regex=True).replace('ด','%B4',regex=True).replace('ต','%B5',regex=True).replace('ถ','%B6',regex=True).replace('ท','%B7',regex=True).replace('ธ','%B8',regex=True).replace('น','%B9',regex=True).replace('บ','%BA',regex=True).replace('ป','%BB',regex=True).replace('ผ','%BC',regex=True).replace('ฝ','%BD',regex=True).replace('พ','%BE',regex=True).replace('ฟ','%BF',regex=True).replace('ภ','%C0',regex=True).replace('ม','%C1',regex=True).replace('ย','%C2',regex=True).replace('ร','%C3',regex=True).replace('ฤ','%C4',regex=True).replace('ล','%C5',regex=True).replace('ฦ','%C6',regex=True).replace('ว','%C7',regex=True).replace('ศ','%C8',regex=True).replace('ษ','%C9',regex=True).replace('ส','%CA',regex=True).replace('ห','%CB',regex=True).replace('ฬ','%CC',regex=True).replace('อ','%CD',regex=True).replace('ฮ','%CE',regex=True).replace('ฯ','%CF',regex=True).replace('ะ','%D0',regex=True).replace('ั','%D1',regex=True).replace('า','%D2',regex=True).replace('ำ','%D3',regex=True).replace('ิ','%D4',regex=True).replace('ี','%D5',regex=True).replace('ึ','%D6',regex=True).replace('ื','%D7',regex=True).replace('ุ','%D8',regex=True).replace('ู','%D9',regex=True).replace('ฺ','%DA',regex=True).replace('฿','%DF',regex=True).replace('เ','%E0',regex=True).replace('แ','%E1',regex=True).replace('โ','%E2',regex=True).replace('ใ','%E3',regex=True).replace('ไ','%E4',regex=True).replace('ๅ','%E5',regex=True).replace('ๆ','%E6',regex=True).replace('็','%E7',regex=True).replace('่','%E8',regex=True).replace('้','%E9',regex=True).replace('๊','%EA',regex=True).replace('๋','%EB',regex=True).replace('์','%EC',regex=True).replace('ํ','%ED',regex=True).replace('๎','%EE',regex=True).replace('๏','%EF',regex=True).replace('๐','%F0',regex=True).replace('๑','%F1',regex=True).replace('๒','%F2',regex=True).replace('๓','%F3',regex=True).replace('๔','%F4',regex=True).replace('๕','%F5',regex=True).replace('๖','%F6',regex=True).replace('๗','%F7',regex=True).replace('๘','%F8',regex=True).replace('๙','%F9',regex=True).replace('๚','%FA',regex=True).replace('๛','%FB',regex=True).replace(' ','%20',regex=True)

def fix_geocodes(x):
	return x.replace("x : y :","").replace("x : ","").replace(" y : ",", ")

def rm_zeropostcode(x):
	return re.sub(r'\b0\b','', x)

def rm_tabs_lines(x):
	return re.sub(r"[\n\t]*", "", x)

class PCDWaste_Listing_Item(Item):
    order = Field(input_processor=Identity(), output_processor=TakeFirst())
    operator_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    operator_href = Field(input_processor=MapCompose(rm_quotes,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    location_name_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    location_href = Field(input_processor=MapCompose(rm_quotes,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    fulladdress_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    address_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    subdistrict_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    district_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    province_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    postcode = Field(input_processor=MapCompose(rm_quotes,rm_whitespace), output_processor=TakeFirst())
    area_rai = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_commas,rm_doublespace), output_processor=TakeFirst())
    type_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    compliance_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
    tons_daily = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_commas,rm_doublespace,rm_na), output_processor=TakeFirst())
    lastupdate = Field(output_processor=TakeFirst())

class PCDWaste_LocalGov_Item(Item):
	local_entity_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
	fulladdress_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
	address_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
	subdistrict_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
	district_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
	province_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
	postcode = Field(input_processor=MapCompose(rm_quotes,rm_whitespace), output_processor=TakeFirst())
	phone = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
	geolocation = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
	administrative_area_th = Field(input_processor=MapCompose(rm_quotes,rm_xa,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
	operator_href = Field(input_processor=MapCompose(rm_quotes,rm_whitespace,rm_doublespace), output_processor=TakeFirst())
	lastupdate = Field(output_processor=TakeFirst())
