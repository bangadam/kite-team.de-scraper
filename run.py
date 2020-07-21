import glob

import requests
import bs4
import json
import pandas
import urllib3
urllib3.disable_warnings()
session = requests.Session()

def get_category_url():
    url = 'http://www.kite-team.de/'
    res = session.get(url)
    res = bs4.BeautifulSoup(res.content, 'html.parser')
    parent_nav = res.find('nav', attrs={'id':'evo-main-nav'})
    category_list = res.findAll('div', class_='caption')
    data_urls = []
    no = 1
    for cl in category_list:
        node = cl.find('a')
        if node is not None:
            print(f'Get category...{no}')
            category = node['href']
            data_urls.append(category)
            no += 1

    return data_urls

def get_category_item_list(category):
    base_url = 'http://www.kite-team.de/'
    res = session.get(base_url+category)
    res = bs4.BeautifulSoup(res.content, 'html.parser')
    all_title = res.findAll('h4', class_="title")
    data_titles = []
    for title in all_title:
        product_link = title.find('a')['href']
        data_titles.append(product_link)
    return data_titles

def get_product_detail(url_product):
    base_url = 'http://www.kite-team.de/'
    res = session.get(base_url+url_product)
    res = bs4.BeautifulSoup(res.content, 'html.parser')
    product_title = res.find('h1', class_='product-title').text
    product_sku = res.find('span', attrs={'itemprop': 'sku'}).text
    product_image = res.find('div', attrs={'id': 'gallery'}).findAll('a')

    data_image = []
    for image in product_image:
        data_image.append('http://www.kite-team.de/'+image['href'])

    product_description = res.find('div', class_='Kite_Beschreibung').text
    return {
        'product_title': product_title,
        'product_sku': product_sku,
        'product_image': data_image,
        'product_description': product_description,
    }

def json_file(response, name_file):
    data = []
    for item in response:
        data.append(item)
    with open(f'./results/category-product/{name_file}.json', 'w') as outfile:
        json.dump(response, outfile)

def json_load(filename):
    with open(filename) as outfile:
        return json.load(outfile)

def html_file(response):
    file = open('response.html', 'w+')
    file.write(response.text)
    file.close()

def csv_file(filename):
    data_product = []
    with open('./results/category-product/'+filename) as outfile:
        data = json.load(outfile)
        data_product = data

    # print(data_product)
    csv = pandas.DataFrame(data_product)
    csv.to_csv(f'./results/csv-file-of-category-product/{filename.replace(".json", "-product")}.csv', index=False)

def get_all_category_product_json_file():
    files = sorted(glob.glob('./results/category-product/*.json'))
    return  files


def run():
    while True:
        menu = ''
        menu += 'https://www.kite-team.de/ SCRAPER \n'
        menu += '===================================\n'
        menu += 'Choose Menu :\n'
        menu += '1. Get All Category \n'
        menu += '2. Get All Item Of Category \n'
        menu += '3. Create CSV file of category product \n'
        menu += 'Input number : '

        option = int(input(menu))
        if option == 1:
            print("Getting All Category...")
            urls = get_category_url()
            with open(f'./results/all_category.json', 'w') as outfile:
                json.dump(urls, outfile)

        elif option == 2:
            print('Getting All Product Of Category...')
            data = json_load('./results/all_category.json')
            temp_product = []
            no = 0;
            for category in data:
                print(f"[{no}] => {category}")
                no += 1
            menu = 'Choose category for scrap: '
            option = int(input(menu))
            choosen_category = ''
            for key,value in enumerate(data):
                if key == option:
                    choosen_category = value

            print(f'Getting {choosen_category} category product..')
            data = get_category_item_list(choosen_category)
            product_detail = []
            no = 1
            for item in data:
                print(f'Getting product detail ...{no}')
                product_detail.append(get_product_detail(item))
                no += 1
            json_file(product_detail, choosen_category)
            print('Done...')

        elif option == 3:
            data = get_all_category_product_json_file()
            choosen_file = ''
            no = 0
            for item in data:
                print(f'[{no}] => {item.replace("./results/category-product/", "")}')
                no += 1
            option = int(input('Choose file: '))
            choose = 0
            for item in data:
                if choose == option:
                    choosen_file = item.replace('./results/category-product/', '')
                choose += 1
            csv_file(choosen_file)
            print('Done...')



if __name__ == "__main__":
    run()