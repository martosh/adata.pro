# ADATA.PRO task/description

# Scrapy Crawler:
## Description:
  
Collects/crawl data from https://gplay.bg/ under "Периферия" and "Хардуер" categories, and all of theirs subcategories.\
The script downloads only products with status "available" and price amount under or equal to 200 leva.\
The collected data for products is stored in json format file and in sqlite DB. The script is built to update the prices of the products if there are any changes.

## DB desc:
>Table[__items__]:\
>(category text, subcategory text, title text, subtitle text, product_number text primary key, price real, source_url text)\

## Settings
The default db file is "gplay.db", it can be edited from the top of "scrp_gplay.py"\
The json schema file for validation the data is called "json_schema.json" it can be edited from the top of "scrp_gplay.py"\
The last parameter from execution `-o result.jl` is the json output file you can name it whatever \<name_output>.jl

## Requirements:
scrapy framework\
scrapy framework structure
## How to execute:
```
scrapy runspider scrp_gplay.py -o result.jl
```

# Django REST API:
## Description:
Creates REST API via django framewor for collected data from https://gplay.bg 

## Requirements:
django
djangorestframework

## First start:

First time starting:\
create link for db(gplay.db) in your main "gplay" django project dir `ls -s <db_path> gplay.db`\
you must make a migration `python manage.py makemigrations`, `python manage.py migrate`\
create super user `python manage.py createsuperuser`\
create new regular user and new token for authentication (from the user admin panel http://127.0.0.1:8000/admin/ - top right corner)


## REST API endpoints and usage:
You must add a custom header that looks like that(where you must replace the token with yours):\
Authorization:  Token 250test_token123123asdasd

`http://127.0.0.1:8000/gapi/items/search/<title>`\
__example__: `http://127.0.0.1:8000/gapi/items/search/JBL`

This will return json data for all titles that match for LIKE %title% in DB\

`http://127.0.0.1:8000/gapi/items/list/` or `http://127.0.0.1:8000/gapi/items/list/?page=<page_num>`\
__example__: `http://127.0.0.1:8000/gapi/items/list/page=2`

For listing 10 products per page

`http://127.0.0.1:8000/gapi/items/<product_code>`\
__example__: `http://127.0.0.1:8000/gapi/items/HAMA-131597`\

And remember Have Fun :)
