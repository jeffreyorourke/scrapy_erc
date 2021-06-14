# -*- coding: utf-8 -*-
# inspect_response(response, self)  # can be useful when debugging
# open_in_browser(response)  # can be useful when debugging

# spider names
pcdwaste_listings = 'pcdwaste_listings'
localgov = 'localgov'

import os
from sqlalchemy import create_engine
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
PORT = 5432
DB = "scrapy_cancan"
dbschema = 'erc'  # refer also to dbschema variable assignment in models.py

POSTGRES_HOST = os.getenv('LENOVO_CHARCOAL_HOST')
# POSTGRES_HOST = os.getenv('LENOVO_GREY_HOST')
# POSTGRES_HOST = os.getenv('VAIO_HOST')
CONNECTION_STRING = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{PORT}/{DB}"

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.exceptions import DropItem
from scrapy.http import TextResponse
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.shell import inspect_response
from scrapy.utils.response import open_in_browser
from scrapy_erc.items import PCDWaste_Listing_Item, PCDWaste_LocalGov_Item, PCDWaste_Location_Item

import numpy as np
import pandas as pd
import io
import uuid
import time
from datetime import datetime, timezone
today = datetime.today().strftime('%Y%m%d')

# for scraping with Selenium and Google translation
drivefolder = "C:/Users/Public/" # local folder for temp files used in transalation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
options = Options()
options.add_argument("--window-size=1920,1080")
options.headless = False

def saveTable(connectionstring, inputtable, dbschema, tablename):
    engine = create_engine(connectionstring, pool_size=10, connect_args={'options': '-csearch_path={}'.format(dbschema)})
    inputtable.head(0).to_sql(tablename, engine, if_exists='replace',index=False)
    conn = engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    inputtable.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    contents = output.getvalue()
    cur.copy_from(output, tablename, null="") # null values become ''
    print(cur.rowcount, 'rows affected')
    conn.commit()
    conn.close()

def getTable(connectionstring, database, dbschema, tabletoget):
    engine = create_engine(connectionstring, pool_size=10, connect_args={'options': '-csearch_path={}'.format(dbschema)})
    conn = engine.raw_connection()
    sql = "SELECT * from " + dbschema + "." + tabletoget + ";"
    table = pd.read_sql_query(sql, conn)
    conn.close()
    return table

def missing_elements(L):  # find missing numbers from sorted list
    start, end = L[0], L[-1]
    return sorted(set(range(start, end + 1)).difference(L))

def TranslateColumns(inputtable, colstotrans, drivefolder, language_source, language_target):
    # launch headless Chromedriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('chromedriver',options=chrome_options)

    # load columns to be translated, cast as string, strip text, and save as xlsx spreadsheet
    text_to_trans = inputtable[colstotrans].copy()
    text_to_trans.to_string(header = True).strip()
    fileuuid = "temp_translation_file_" + str(uuid.uuid4()) + ".xlsx"
    text_to_trans.to_excel(drivefolder + fileuuid)

    # populate Google Translate url with chosen parameters and get url
    url = "https://translate.google.com/?sl=" + language_source + "&tl=" + language_target + "&op=docs"
    driver.get(url)

    # send xlsx file to be translated directly to button (skipping upload file dialogue window) and click translate button
    filepath = drivefolder + fileuuid
    Browse_Btn = driver.find_element_by_xpath('//*[@id="i34"]').send_keys(filepath)
    ActionChains(driver).move_to_element(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//html/body/c-wiz/div/div[2]/c-wiz/div[3]/c-wiz/div[2]/c-wiz/div/form/div[2]/div[2]/button/span')))).click().perform()

    # wait for visibility then invisibility of second "Translating" spinner '//*[@id="gt-dt-spinner"]'
    try:
        visiblewait = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="gt-dt-spinner"]')))
    except:
        pass
    invisiblewait = WebDriverWait(driver, 20000).until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="gt-dt-spinner"]')))  # wait 30 mins or so for translation to finish

    # read Google Translate results page, generate target column names and rename column(s)
    transresult = pd.read_html(driver.page_source, header=0)[0].drop("Unnamed: 0", axis=1) #get all tables on page
    # colstransnames = [sub + '_' + language_target for sub in transresult] #generate target col names
    # transresult.columns = colstransnames
    transresult.columns = transresult.columns.str.replace("_th","")
    result = inputtable.join(transresult) #join and drop 'index' column
    os.remove(filepath)
    driver.close()
    return result

class PCDWaste_Listings_Selenium(scrapy.Spider):
    handle_httpstatus_list = [401]
    name = pcdwaste_listings

    def start_requests(self):
        url = "https://thaimsw.pcd.go.th/index.php"
        yield scrapy.Request(
            url=url,
            callback=self.parse_listing)

    def parse_listing(self, response):
        pcdwaste_listing_item = PCDWaste_Listing_Item()

        # Launch Chromedriver browser
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # do not wait for page to stop loading (it never does!)
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"
        self.driver = webdriver.Chrome('chromedriver', desired_capabilities=capa, options=chrome_options)
        self.driver.set_window_size(968,1030)
        self.driver.set_window_position(0,0)
        wait = WebDriverWait(self.driver, 1)

        url = "https://thaimsw.pcd.go.th/index.php"
        self.driver.get(url)
        Wait = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="section2"]/div/div/div[2]/div[1]/div[2]/table/tbody')))

        # # remove popup
        # driver.execute_script("window.stop();")
        # WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="exampleModal"]/div/div/div[1]/button/span'))).click()

        while True:
            time.sleep(1)
            Wait = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="section2"]/div/div/div[2]/div[1]/div[2]/table/tbody')))
            Wait = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="section2"]/div/a/button')))
            response = TextResponse(url=url, body=self.driver.page_source, encoding='utf-8')
            rows = response.xpath('//*[@id="section2"]/div/div/div[2]/div[1]/div[2]/table/tbody')
            for row in rows:
                l = ItemLoader(item=PCDWaste_Listing_Item(), selector=row)
                l.add_xpath('order', './/tr/td[1]//text()')
                l.add_xpath('operator_th', './/tr/td[2]//text()')
                l.add_xpath('operator_href', './/tr/td[2]/a//@href')
                l.add_xpath('location_name_th', './/tr/td[3]//text()')
                l.add_xpath('location_href', './/tr/td[3]/a//@href')
                l.add_xpath('fulladdress_th', './/tr/td[4]//text()')
                l.add_xpath('address_th', './/tr/td[4]//text()', re=r'(.+?(?=อ\.))')  # everything up to " ต."
                l.add_xpath('subdistrict_th', './/tr/td[4]//text()', re=r'(?<=ต\. ).*?(?= อ\.)') # everything between "ต. " and " อ."
                l.add_xpath('district_th', './/tr/td[4]//text()', re=r'(?<=อ\. ).*?(?= จ\.)') # everything between "อ. " and " จ."
                l.add_xpath('province_th', './/tr/td[5]//text()')
                l.add_xpath('postcode', './/tr/td[4]//text()', re=r'(\d+)(?!.*\d)')  # regex number if number at end of string
                l.add_xpath('area_rai', './/tr/td[6]//text()')
                l.add_xpath('type_th', './/tr/td[7]//text()')
                l.add_xpath('compliance_th', './/tr/td[8]//text()')
                l.add_xpath('tons_daily', './/tr/td[9]//text()')
                l.add_value("lastupdate", datetime.now(timezone.utc))
                yield l.load_item()
            try: # click next page
                element = self.driver.find_element_by_xpath("//span[@class='sr-only' and text()='Next']")
                action = ActionChains(self.driver)  # create action chain object
                action.click(on_element = element)  # click the item
                action.perform()  # perform the operation
                print("Navigating to Next Page")
                time.sleep(1)
            except:
                print("Last Page Reached")
                break

        self.driver.close()
        return None

class Local_Government(scrapy.Spider):
    handle_httpstatus_list = [401]
    name = localgov

    def start_requests(self):
        url = 'https://thaimsw.pcd.go.th/index.php'
        yield scrapy.Request(
            url=url,
            callback=self.parse)

    def parse(self, response):
        # get urls to scrape
        tabletoget = 'pcdwaste_listing'
        listings = getTable(CONNECTION_STRING, DB, dbschema, tabletoget) # [0:5]  # xxx Local_Government Throttle
        operator_hrefs = listings.operator_href
        for operator_href in operator_hrefs:
            url = "https://thaimsw.pcd.go.th/" + str(operator_href)
            yield scrapy.Request(
                url=url,
                meta = {"url": url, "operator_href": operator_href},
                callback=self.parse_detail)

    def closed(self, reason):

        # Translation
        self.logger.info("*** Starting Translation ***")
        tabletoget = 'pcdwaste_localgov'
        listings = getTable(CONNECTION_STRING, DB, dbschema, tabletoget)  # def getTable(connectionstring, database, dbschema, tabletoget)

        # get English translations of column using Google Translate
        inputtable = listings[['operator_no','local_entity_th','fulladdress_th','address_th','province_th','administrative_area_th']] # xxx Local_Government translation throttle
        colstotrans = ['local_entity_th','fulladdress_th','address_th','province_th','administrative_area_th'] # choose columns to be translated
        drivefolder = "C:/Users/Public/" # choose local folder for temp file - if files on local Jupyter drive use: drivefolder = ""
        language_source = 'th' # choose translate from language ('auto' or ISO 639-1 such as 'th')
        language_target = 'en' # choose translate to language (ISO 639-1 such as 'en'))
        listings2 = TranslateColumns(inputtable, colstotrans, drivefolder, language_source, language_target)
        listings2 = listings2.replace(r'\r+|\n+|\t+','', regex=True)

        # connect to database
        engine = create_engine(CONNECTION_STRING, pool_size=10, connect_args={'options': '-csearch_path={}'.format(dbschema)})
        listings2.head(0).to_sql('translations', engine, if_exists='replace',index=False)
        conn = engine.raw_connection()
        cur = conn.cursor()
        output = io.StringIO()

        # drop old table and create empty new table
        listings2.to_csv(output, sep='\t', header=False, index=False)
        output.seek(0)
        contents = output.getvalue()
        cur.copy_from(output, 'translations', null="") # null values become ''
        self.logger.info('*** ' + str(cur.rowcount) + ' Records Translated ***')
        conn.commit()

        cur.execute("""
            UPDATE """ + dbschema + """.""" + tabletoget + """ cp
                SET local_entity = s.local_entity, fulladdress = s.fulladdress, address = s.address, province = s.province, administrative_area = s.administrative_area
                FROM """ + dbschema + """.translations s
                WHERE cp.operator_no = s.operator_no
                RETURNING s.local_entity,s.fulladdress,s.address,s.province,s.administrative_area;
                DROP TABLE IF EXISTS """ + dbschema + """.translations;
                """)
        conn.commit()
        self.logger.info("*** Translations Committed to Source Table ***")
        cur.close()
        conn.close()

        # lookup addresses in th_postalcodes_20210530 reference file
        self.logger.info("*** Starting Address Lookup ***")

        # get listings and create lookup field
        tabletoget = 'pcdwaste_localgov'
        # listings = getTable(CONNECTION_STRING, DB, dbschema, tabletoget)  # def getTable(connectionstring, database, dbschema, tabletoget)
        # thaddresses = listings[['operator_no','subdistrict_th','district_th','province_th']]
        thaddresses = getTable(CONNECTION_STRING, DB, dbschema, tabletoget)[['operator_no','subdistrict_th','district_th','province_th']]  # def getTable(connectionstring, database, dbschema, tabletoget)
        thaddresses['subdistrict_th~district_th~province_th'] = thaddresses['subdistrict_th'] + "~" + thaddresses['district_th'] + "~" + thaddresses['province_th']

        # get th_postalcodes_20210530 reference file and merge selected fields
        tabletoget_postcodes = 'th_postalcodes_20210530'
        th_postalcodes_20210530 = getTable(CONNECTION_STRING, DB, dbschema, tabletoget_postcodes)  # def getTable(connectionstring, database, dbschema, tabletoget)
        thaddresses2 = pd.merge(thaddresses, th_postalcodes_20210530[['subdistrict_th~district_th~province_th','postalcode','subdistrict_en','district_en','province_en',
            'region_en','latitude','longitude']], on = 'subdistrict_th~district_th~province_th', how = 'left').drop(columns='subdistrict_th~district_th~province_th')

        # rename columns to match target database
        thaddresses2.rename(columns={'subdistrict_en':'subdistrict', 'district_en':'district', 'province_en':'province', 'postalcode':'postcode',
            'region_en':'region', 'latitude':'latitude_lookup', 'longitude':'longitude_lookup'}, inplace=True)
        # thaddresses3 = thaddresses2.replace(r'\r+|\n+|\t+','', regex=True)

        # connect to database
        engine = create_engine(CONNECTION_STRING, pool_size=10, connect_args={'options': '-csearch_path={}'.format(dbschema)})
        thaddresses2.head(0).to_sql('thaddresses2', engine, if_exists='replace',index=False)
        conn = engine.raw_connection()
        cur = conn.cursor()
        output = io.StringIO()

        # drop old and create new staging table
        thaddresses2.to_csv(output, sep='\t', header=False, index=False)
        output.seek(0)
        contents = output.getvalue()
        cur.copy_from(output, 'thaddresses2', null="") # null values become ''
        self.logger.info('*** ' + str(cur.rowcount) + ' Address Records Parsed ***')
        conn.commit()
        # conn.close()

        cur.execute("""
           UPDATE """ + dbschema + """.""" + tabletoget + """ cp
            SET subdistrict = s.subdistrict, district = s.district, province = s.province, region = s.region, latitude_lookup = s.latitude_lookup, longitude_lookup = s.longitude_lookup
            FROM """ + dbschema + """.thaddresses2 s
            WHERE cp.operator_no = s.operator_no
            RETURNING s.subdistrict, s.district, s.province, s.region, s.latitude_lookup, s.longitude_lookup;
            DROP TABLE IF EXISTS """ + dbschema + """.thaddresses2;
            """)

        self.logger.info("*** Address Lookups Appended ***")
        conn.commit()
        # cur.close()
        conn.close()

        return None

    def parse_detail(self,response):
        url = response.meta["url"]
        operator_href = response.meta["operator_href"]
        pcdwaste_localgov_item = PCDWaste_LocalGov_Item()
        page = response.xpath('//html/body/div[2]/div[1]/div')
        l = ItemLoader(item=PCDWaste_LocalGov_Item(), selector=page)
        l.add_xpath('local_entity_th', './/div[1]/h2/text()[1]')
        l.add_xpath('fulladdress_th', './/h4[contains(text(),"ที่ตั้งสำนักงาน")]/following-sibling::div/text()[2]')
        l.add_xpath('address_th', './/h4[contains(text(),"ที่ตั้งสำนักงาน")]/following-sibling::div/text()[2]', re=r'(.+?(?=ต\.))')  # everything up to " ต."
        l.add_xpath('subdistrict_th', './/h4[contains(text(),"ที่ตั้งสำนักงาน")]/following-sibling::div/text()[2]', re=r'(?<=ต\. ).*?(?= อ\.)') # everything between "ต. " and " อ."
        l.add_xpath('district_th', './/h4[contains(text(),"ที่ตั้งสำนักงาน")]/following-sibling::div/text()[2]', re=r'(?<=อ\. ).*?(?= จ\.)') # everything between "อ. " and " จ."
        l.add_xpath('province_th', './/h4[contains(text(),"ที่ตั้งสำนักงาน")]/following-sibling::div/text()[2]', re=r'(?<=จ\. ).*?(?=\s)') # regex between "จ. " and space " "
        l.add_xpath('postcode', './/h4[contains(text(),"ที่ตั้งสำนักงาน")]/following-sibling::div/text()[2]', re=r'(\d+)(?!.*\d)')  # regex number if number at end of string
        l.add_xpath('phone', './/h4[contains(text(),"ที่ตั้งสำนักงาน")]/following-sibling::div/text()[3]', re=r'(?<=โทรศัพท์).*?(?=โทรสาร)')
        l.add_xpath('geolocation', './/div[2]/div[1]/div[2]/div//text()')
        l.add_xpath('administrative_area_th', './/div[2]/div[1]/div[3]/div/text()')
        l.add_value('operator_href', operator_href)
        l.add_value("lastupdate", datetime.now(timezone.utc))
        yield l.load_item()

        return None
