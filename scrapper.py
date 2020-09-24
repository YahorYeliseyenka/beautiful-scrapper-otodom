import time
import traceback
from math import ceil

import progressbar as pb
import json
from urllib.parse import urlparse
from urllib.request import Request, urlopen, HTTPError, urlretrieve
from bs4 import BeautifulSoup as bs

from offer import Offer

offersPerPage = 24
backslash = '\\'


# return parsed html file
def download_page(url):
    request = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 '+
                        '(KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
    sauce = urlopen(request).read()
    soup = bs(sauce.decode('utf-8', 'ignore'), 'lxml')
    return soup


# return amount of ofers in specific category
def get_offers_amount(html_page):
    offers_amount = (html_page.find('div', class_='offers-index').find('strong').text)
    return int(''.join(offers_amount.split()))


# return list of offers in page
def get_offers(html_page):
    div_container = html_page.find('div', class_='listing')
    offers = []
    for article in div_container.find_all('article', class_='offer-item'):
        offers.append(get_offer_info(article.get('data-url')))
    return offers


def get_page_url(url, page_number):
    return url if page_number == 1 else f'{url}&page={page_number}'


# download info about offer
# return new Offert object with all info OR empty object with page url
def get_offer_info(url):
    html_page = download_page(url)

    #find application/Json script
    appJson = html_page.find(id='server-app-state') if html_page else None

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

        name = initialProps.get('meta', {}).get('seo', {}).get('title')

        location = advert_data.get('location', {})
        address = location.get('address')
        coordinates = [location.get('coordinates', {}).get(item) for item in ('latitude', 'longitude')]
        geo_level = {item.get('type'):item.get('label') for item in location.get('geoLevel', [])}

        characteristics = {item.get('key'):item.get('value') 
                            for item in advert_data.get('characteristics', [])}

        price = {i:advert_data.get('price', {}).get(i) for i in ('value', 'unit', 'suffix')}

        features=advert_data.get('features', [])
        features_en = meta_data.get('Equipment_types', []) + meta_data.get('Security_types', [])
        features_en += meta_data.get('Media_types', []) + meta_data.get('Extras_types', [])
        if features:
            if len(features) > len(features_en):
                if features_en:
                    features_en += features[:-len(features_en)]
                else:
                    features_en = features

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


#converts list of offers into json and save
def save_offers(dir_, appartmentArray, fileName):
    with open(f'{dir_}/page{fileName}.json', 'w', encoding='utf-8') as outfile:
        for appartment in appartmentArray:
            json.dump(appartment.__dict__, outfile, indent=1, 
                        separators=(',', ': '), ensure_ascii=False)
       

def proceed(urls_dirs):
    total_pages, total_offers, total_saved = (0, 0, 0)
    pages_with_error = []

    for url in urls_dirs:
        offers_amount = get_offers_amount(download_page(url))
        total_offers += offers_amount
        total_pages+= ceil(offers_amount/offersPerPage)
    print(f'{total_offers} offers were found.')

    print('\nProcessing started at', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # initialize progress bar
    timer = pb.ProgressBar(widgets=['', pb.Percentage(), ' ', pb.Bar(fill='-'), ' ', 
                                    pb.ETA()], maxval=total_pages).start()
    counter = 0

    for url, dir_ in urls_dirs.items():
        pages_with_error = []
        pages_amount = ceil(get_offers_amount(download_page(url))/offersPerPage)
        total_saved += pages_amount
        for i in range(1, pages_amount+1):
            page_url = get_page_url(url, i)
            try:
                offers = get_offers(download_page(page_url))
                save_offers(dir_, offers, i)
                counter += 1
                timer.update(counter)   
            except HTTPError:
                pages_with_error.append(page_url)
            except Exception:
                print(f'\nHouston, we have a problem in loop 1 with {page_url}')
                traceback.print_exc()
                counter += 1
                timer.update(counter)
        for url in pages_with_error:
            try:
                offers = get_offers(download_page(url))
                save_offers(dir_, offers, i)
                counter += 1
                timer.update(counter)
            except Exception:
                print(f'\nHouston, we have a problem in loop 2 with {url}')
                traceback.print_exc()
                counter += 1
                timer.update(counter)
        print(f'\n{dir_.split(backslash)[-1].upper()} download completed.', 
                f'\t{pages_amount} pages saved.',
                f'\tProgress: {total_saved} out of {total_pages}.', 
                f'\tEnded at: {timer.last_update_time}.\n')
    timer.finish()
    print(f'Processing ended at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}.\tHAVE A FUN!')
