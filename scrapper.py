import time
from math import ceil

import progressbar as pb
import json
from urllib.parse import urlparse
from urllib.request import Request, urlopen, HTTPError, urlretrieve
from bs4 import BeautifulSoup as bs

from apartment import Apartment

counter = 0


def download_page(url):
    request = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 '+
                        '(KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
    sauce = urlopen(request).read()
    soup = bs(sauce.decode('utf-8', 'ignore'), 'lxml')
    return soup


# return amount of ofers in specific category
def get_page_offers_amount(html_page):
    offers_amount = (html_page.find('div', class_='offers-index').find('strong').text)
    return int(''.join(offers_amount.split()))


# return list of apartments in page
def get_apartments(html_page):
    div_container = html_page.find('div', class_='listing')
    apartments = []
    for article in div_container.find_all('article', class_='offer-item'):
        apartments.append(get_offer_info(article.get('data-url')))
    return apartments


def get_page_url(main_url, page_number):
    return main_url if page_number == 1 else f'{main_url}&page={page_number}'


def get_offer_info(offer_url):
    html_page = download_page(offer_url)

    # pictureContainer = html_page.find('picture')  # find picture container
    appJson = html_page.find(id='server-app-state') #find application/Json script

    if appJson:
        meta_data = json.loads(appJson.text).get('initialProps', {}).get('meta', {}).get('target', {}) or {}
        advert_data = json.loads(appJson.text).get('initialProps', {}).get('data', {}).get('advert', {}) or {}
        
        photos = []
        for photo in advert_data.get('photos', []):
            photos.append(photo.get('large') or 
                            photo.get('medium') or 
                            photo.get('small') or 
                            photo.get('thumbnail'))

        name = json.loads(appJson.text).get('initialProps', {}).get('meta', {}).get('seo', {}).get('title')

        location = advert_data.get('location', {})
        address = location.get('address')
        coordinates = [location.get('coordinates', {}).get(item) for item in ('latitude', 'longitude')]
        geo_level = {item.get('type'):item.get('label') for item in location.get('geoLevel', [])}

        characteristics = {item.get('key'):[item.get('value'), item.get('label')] 
                            for item in advert_data.get('characteristics', [])}

        price = {i:advert_data.get('price', {}).get(i) for i in ('value', 'unit', 'suffix')}

        features_en = meta_data.get('Equipment_types', []) + meta_data.get('Security_types', [])
        features_en += meta_data.get('Media_types', []) + meta_data.get('Extras_types', [])

        extra = {item:advert_data.get(item) for item in ('advertiser_type', 'advert_type', 'agency')}

    return Apartment(url=offer_url, 
                    name=name, 
                    description=advert_data.get('description'),
                    photos=photos, 
                    address=address,
                    coordinates=coordinates,
                    geo_level=geo_level,
                    characteristics=characteristics,
                    price=price,
                    features=advert_data.get('features'),
                    features_en = features_en,
                    owner=advert_data.get('advertOwner'),
                    extra=extra,
                    date_created=advert_data.get('dateCreated'),
                    date_modified=advert_data.get('dateModified')
                    ) if appJson else Apartment(url=offer_url)


#converts list of apartments into json and save
def save_apartments(main_dirs, appartmentArray, fileName):
    with open(main_dirs[0] + '/page' + str(fileName) + '.json', 'w', encoding='utf-8') as outfile:
        for appartment in appartmentArray:
            if main_dirs[1]:
                appartment.photos = save_photos(main_dirs[1], appartment.photos) 
            json.dump(appartment.__dict__, outfile, indent=1, 
                        separators=(',', ': '), ensure_ascii=False)


def save_photos(main_img_dir, photos):
    photo_names = []
    for photo in photos:
        urlretrieve(photo, f'{main_img_dir}/{urlparse(photo).path.split("/")[-2]}.jpg')
        photo_names.append(urlparse(photo).path.split('/')[-2])
    return photo_names
    

def save_all_page_items(i, main_url, main_dirs, timer, pages_with_error=[]):
    global counter
    page_url = get_page_url(main_url, i)
    try:
        apartments = get_apartments(download_page(page_url))
        save_apartments(main_dirs, apartments, i)
        counter += 1
        timer.update(counter)
    except HTTPError:
        pages_with_error.append(i)
    except Exception as error:
        print(f'Houston, we have a problem with {page_url}:\n\t\t{error}')
        counter += 1


def proceed(main_urls_and_dirs):
    all_offers_amount = 0
    for url in main_urls_and_dirs:
        html_page = download_page(url)
        all_offers_amount += get_page_offers_amount(html_page)
    all_pages_amount = ceil(all_offers_amount/24)
    print(f'There will be processed {all_pages_amount} pages with {all_offers_amount} offers')

    # initialize progress bar
    timer = pb.ProgressBar(widgets=[f'Time for loop of {all_pages_amount} iterations: ', 
                                    pb.Percentage(), ' ', pb.Bar(), ' ', 
                                    pb.ETA()], 
                            maxval=all_pages_amount).start()

    for main_url, main_dirs in main_urls_and_dirs.items():
        pages_with_error = []
        for i in range(1, get_page_offers_amount(html_page)+1):
            save_all_page_items(i, main_url, main_dirs, timer, pages_with_error)
        for i in pages_with_error:
            save_all_page_items(i, main_url, main_dirs, timer)
        timer.finish()
