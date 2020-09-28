import os
import time
import traceback
import shutil
from math import ceil

import progressbar as pb
import json
from urllib.parse import urlparse
from urllib.request import Request 
from urllib.request import urlopen, urlretrieve
from urllib.request import HTTPError, URLError
from bs4 import BeautifulSoup as bs

from offer import Offer

dataPath = f'{os.getcwd()}\data'                    # path for the data dir in project folder
offersPerPage = 24                                  # offers on page. 24 - standard. 48, 72
otodomStuff = 'otodompl-imagestmp.akamaized.net'    # otodom.pl 3D image.


# return parsed html file
def download_page(url):
    try:
        request = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 '+
                            '(KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
        sauce = urlopen(request).read()
        soup = bs(sauce.decode('utf-8', 'ignore'), 'lxml')
    except HTTPError:
        soup = None
    return soup


# return amount of ofers in specific category
def get_offers_amount(url):
    html = download_page(url)
    offers_amount = html.find('div', class_='offers-index').find('strong').text if html else '0'
    return int(''.join(offers_amount.split()))


# return list of offers on page
def get_offers(url):
    html = download_page(url)
    div_container = html.find('div', class_='listing')
    offers = []
    for article in div_container.find_all('article', class_='offer-item', attrs={"data-featured-name": "listing_no_promo"}):
        offers.append(get_offer_info(article.get('data-url')))
    return offers


# generate page url
def get_page_url(url, page_number):
    return url if page_number == 1 else f'{url}&page={page_number}'


# download offer info
# return new Offert object with all info OR empty object with page url
def get_offer_info(url):
    html = download_page(url)

    # find application/Json script
    appJson = html.find(id='server-app-state') if html else None

    if appJson:
        initialProps = json.loads(appJson.text).get('initialProps') or {}
        meta_data = initialProps.get('meta', {}).get('target') or {}
        advert_data = initialProps.get('data', {}).get('advert') or {}
        
        photos = []
        for photo in advert_data.get('photos', []):
            photos.append(photo.get('large') or 
                            photo.get('medium') or 
                            photo.get('small') or 
                            photo.get('thumbnail'))

        # offers title
        name = initialProps.get('meta', {}).get('seo', {}).get('title')

        location = advert_data.get('location', {})
        address = location.get('address')
        coordinates = [location.get('coordinates', {}).get(item) for item in ('latitude', 'longitude')]

        # region, city, distinct, sub-region
        geo_level = {item.get('type'):item.get('label') for item in location.get('geoLevel', [])}

        # rent, rooms number, heating type and others
        characteristics = {item.get('key'):item.get('value') 
                            for item in advert_data.get('characteristics', [])}

        price = {i:advert_data.get('price', {}).get(i) for i in ('value', 'unit', 'suffix')}

        # dishwasher, fridge, oven and others
        features=advert_data.get('features', [])
        features_en = meta_data.get('Equipment_types', []) + meta_data.get('Security_types', [])
        features_en += meta_data.get('Media_types', []) + meta_data.get('Extras_types', [])
        if features:
            if len(features) > len(features_en):
                if features_en:
                    features_en += features[:-len(features_en)]
                else:
                    features_en = features
        # advertiser type: private, business...; agency data; advert type
        extra = {item:advert_data.get(item) for item in ('advertiser_type', 'advert_type', 'agency')}

    return Offer(url=url, 
                    name=name, 
                    description=advert_data.get('description'),
                    photos=photos, 
                    address=address,
                    coordinates=coordinates,
                    geo_level=geo_level,
                    characteristics=characteristics,
                    price=price,
                    features=features_en,
                    owner=advert_data.get('advertOwner'),
                    extra=extra,
                    date_created=advert_data.get('dateCreated'),
                    date_modified=advert_data.get('dateModified')
                    ) if appJson else Offer(url=url)


# converts list of offers into json and save
def save_offers(dir_, appartments, file_name):
    with open(f'{get_path(dir_)}/page{file_name}.json', 'w', encoding='utf-8') as outfile:
        json.dump([appartment.__dict__ for appartment in appartments], outfile, indent=1)


# returt amount of objects from JSON file
def count_obj(filenames):
    obj_amount = 0
    for filename in filenames:
        with open(f'{dataPath}\{filename}.json', encoding='utf8') as json_file:
            obj_amount += len(json.load(json_file))
    return obj_amount


# save photos and return a list of their names
def download(urls, photos_path):
    names = []
    for url in urls:
        # there is no need to download 3d objects
        if otodomStuff in url:
            names.append('')
        else:
            name = urlparse(url).path.split('/')[-2]+'.jpg'
            try:
                urlretrieve(url, f'{photos_path}\{name}')
                names.append(name)
            except Exception as e:
                names.append('')
                print('\nDoes not exist:',url)
    return names


# save photos
def save_photos(filenames):
    obj_amount = count_obj(filenames)
    print(f'\n{obj_amount} objects with photos will be processed.')
    print('Photos downloading and saving process STARTED at', 
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    timer = pb.ProgressBar(widgets=['Progress:', pb.Bar(fill='-'), 
                            ' Complete: ', pb.SimpleProgress(), ' ', 
                            pb.ETA()], maxval=obj_amount).start()
    counter = 0

    for filename in filenames:
        photos_path = f'{dataPath}\{filename}-img'
        json_path = f'{dataPath}\{filename}.json'
        create_dir(photos_path)
        data = []

        with open(json_path, encoding="utf8") as json_file:
            data = json.load(json_file)

        for obj in data:
            obj['photos'] = download(obj['photos'] or [], photos_path)
            counter += 1
            timer.update(counter)

        with open(json_path, 'w', encoding="utf8") as outfile:
            json.dump(data, outfile, indent=1)

        print(f'\nPhotos were successfully saved in the {filename}-img directory.', 
                f'{filename}.json updated.')
    print('\nPhotos downloading and saving process ENDED at', 
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        

# create project data dir for scrapper results
def create_dir(path):
    if not os.path.exists(path): os.mkdir(path)


def get_path(dir_):
    return f'{dataPath}\{dir_}'


# combine all data from a specific category into one file
def to_one_file(dir_):
    path = get_path(dir_)
    for (dirpath, dirnames, filenames) in os.walk(path):
        data = []

        for filename in filenames:
            with open(f'{path}\{filename}', encoding="utf8") as json_file:
                data += json.load(json_file)

        with open(f'{dataPath}\{dir_}.json', 'w', encoding="utf8") as outfile:
            json.dump(data, outfile, indent=1)

        shutil.rmtree(path)


def get_pages_amount(url):
    return ceil(get_offers_amount(url)/offersPerPage)


def proceed(urls_dirs, savephotos):
    total_pages = 0
    pages_with_error = []

    create_dir(dataPath)

    for url in urls_dirs:
        total_pages += get_pages_amount(url)
    print(f'\n{total_pages} pages will be dowloaded and saved.')

    if total_pages != 0:
        print('Data gathering process STARTED at', 
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), '\n')
        # initialize progress bar
        timer = pb.ProgressBar(widgets=['Progress:', pb.Bar(fill='-'), 
                                ' Complete: ', pb.SimpleProgress(), ' ', 
                                pb.ETA()], maxval=total_pages).start()
        timer_counter = 0

        for url, dir_ in urls_dirs.items():
            create_dir(get_path(dir_))
            
            pages_with_error = []
            pages_amount = get_pages_amount(url)

            for i in range(1, pages_amount+1):
                page_url = get_page_url(url, i)
                try:
                    offers = get_offers(page_url)
                    save_offers(dir_, offers, i)
                    timer_counter += 1
                    timer.update(timer_counter)   
                except (HTTPError, URLError, AttributeError):
                    pages_with_error.append((page_url,i))
                except Exception:
                    print(f'\nHouston, we have a problem in loop 1 with {page_url}')
                    traceback.print_exc()
                    timer_counter += 1
                    timer.update(timer_counter)
            for url_error, i in pages_with_error:
                try:
                    offers = get_offers(url_error)
                    save_offers(dir_, offers, i)
                    timer_counter += 1
                    timer.update(timer_counter)
                except Exception:
                    print(f'\nHouston, we have a problem in loop 2 with {url_error}')
                    traceback.print_exc()
                    timer_counter += 1
                    timer.update(timer_counter)

            to_one_file(dir_)
            print(f'\n{dir_}.json saved successfully.')
            
        print('\nData gathering process ENDED at', 
                {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

        if savephotos: save_photos(urls_dirs.values())
