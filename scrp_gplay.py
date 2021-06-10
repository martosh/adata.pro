#!/usr/bin/python3
import scrapy
import logging
import re
import json
from itemadapter import ItemAdapter
import jsonschema 
import sqlite3
from sqlite3 import Error
import os

######################
#### start with ####
#scrapy runspider scrp_gplay.py -o result.jl

#######################
# read schema once
#######################
def get_schema(jfile):
    if not os.path.isfile('./' + jfile):
          raise OSError(f"json schema file[{jfile}] is missing!")

    with open(jfile, 'r') as file:
        schema = json.load(file)
    return schema

json_schema = get_schema('json_schema.json')

######################
# sqlite
######################
def connect_db(db_file):
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    csr = conn.cursor()
    csr.execute('''CREATE TABLE IF NOT EXISTS items
    (category text, subcategory text, title text, subtitle text, product_number text primary key, price real, source_url text)''')
   
    db_price_indexes = {}

    for row in csr.execute('SELECT product_number, price FROM items'):
        db_price_indexes[row[0]] = row[1]

    return conn, csr, db_price_indexes

conn, csr, db_price_indexes = connect_db('gplay.db')

##################################
class GplaySpider(scrapy.Spider):
    name = 'gplay'
    start_urls = [ 'https://gplay.bg/гейминг-периферия', 'https://gplay.bg/гейминг-хардуер' ]

    custom_settings = {
            'FEED_EXPORT_ENCODING' : 'utf-8',
            'DOWNLOAD_FAIL_ON_DATALOSS' : 'False',
            'ITEM_PIPELINES' : {
                'scrp_gplay.JsonValidationPipeline': 300,
                'scrp_gplay.AddToDbPipeline': 400,
        }
    }  

    ###########################
    def parse(self, response):

        #follow sub-cats
        for sub_cat_url in response.css("div.categories-grid-item").css('a::attr(href)').getall():

            if sub_cat_url is not None:
                yield scrapy.Request(sub_cat_url, callback=self.parse_sub_cat)

    ###########################
    def parse_sub_cat(self, response):

        #follow products url if available or cheeper then 200 BGN
        for product in response.css("div.product-item"):

            product_url    = product.css('a::attr(href)').get()
            product_status = product.css('div.product-status::attr(title)').get()
            product_price  = self._normal_price( product)

            if 'наличен' in product_status and product_price <= 200:
                if product_url is not None:
                    yield scrapy.Request(product_url, callback=self.parse_product, cb_kwargs={'price' : product_price} )

        next_page = response.css("ul.pagination").css('a::attr(href)').get()

        if next_page is not None:
            yield response.follow(next_page, self.parse_sub_cat)

    ###########################
    def parse_product(self, response, price):
        #take product data
        data = {
        'category'      : response.css('.py-3').css('a::text')[1].get(),
        'subcategory'   : response.css('.py-3').css('a::text')[2].get(),
        'title'         : response.css('.py-3').css('a::text')[3].get(),
        'subtitle'      : response.css('.product-subtitle::text').get(),  
        'product_number': response.css('.product-ref-number').css("strong::text").get(), 
        'price'         : price,
        'source_url'    : response.url,
        }

        #do some more cleaning
        for key in data.keys():
          if isinstance(data[key], str):
            data[key] = data[key].strip();

        yield data;
        #logging.warning(" Show me data :" )
        #logging.warning( data )
    
    ###################
    # format price 
    ###################
    def _normal_price(self, product_body):

        product_price = product_body.css('div.normal-price').css('price').get()

        if product_price is not None:
            product_price = re.findall(r'="([^"]+?)"', product_price)[0]
        else:
            product_price = None;

        return float(product_price)
            
############################
# JsonValidation Class PipeL
############################
class JsonValidationPipeline:

    def process_item(self, item, spider):
        item = ItemAdapter(item).asdict()
        try: 
            jsonschema.validate(instance=item, schema=json_schema)
        except jsonschema.exceptions.ValidationError as e:
            print( f"Error: invalid json against schema:[{e}]")
        else:
            print('test');

        return item

############################
# Data to DB PipeL
############################
class AddToDbPipeline:

    def process_item(self, item, spider):
        item = ItemAdapter(item).asdict()
        product_n = item['product_number']

        #NOTE execute commit here or at the end -  depends how stable is the app/web-site
        if product_n in db_price_indexes:

            #update if prod exists and price diff
            if item['price'] != db_price_indexes[product_n]:
                sql = "UPDATE items SET price = ? WHERE product_number = ?"
                udata = (item['price'], product_n)
                csr.execute(sql, udata)
                conn.commit()
        else:
            data = (item['category'], item['subcategory'], item['title'], item['subtitle'], item['product_number'],item['price'], item['source_url'] )
            sql = ''' INSERT INTO items (category, subcategory, title, subtitle, product_number, price, source_url )  VALUES(?,?,?,?,?,?,?) '''
            csr.execute(sql, data)
            conn.commit()

        return item

####################
# commit close
####################
conn.commit()
#conn.close() #closes anyway
