import os
import time

import argparse
from urllib.parse import ParseResult

from scrapper import proceed 

dataPath = f'{os.getcwd()}\data'
hostURL = 'www.otodom.pl'
offersPerPage = 24
typesPL = {'renting': 'wynajem',
                'selling': 'sprzedaz',
                'house': 'dom',
                'flat': 'mieszkanie'}


# setup argumet parser with 4 arguments: propertytype, rentaltype, city, image
def get_args():
    parser = argparse.ArgumentParser(description='Provide input scrapper args')
    parser.add_argument('-rt', '--rentaltype', nargs='+', required=True,
                        help='Enter whether you are interested in *renting* or *selling*',
                        type=lambda input: is_valid(parser, ("renting", "selling"), input))
    parser.add_argument('-pt', '--propertytype', nargs='+', required=True,
                        help='Enter whether you are interested in a *house* or *flat*',
                        type=lambda input: is_valid(parser, ('house', 'flat'), input))
    parser.add_argument('-c', '--city', nargs='+', required=True,
                        help='Enter the city you are interested in')
    parser.add_argument('-i', '--image', type=bool, default=False,
                        help='Enter whether you are interested in image scrapping')
    return parser.parse_args()


# function checks if arguments passed from console arr correct
def is_valid(parser, choices, input):
    return input if input in choices else parser.error("Args doesn't equal to {}".format(choices))


# function creates project data dirs for scrapper results
def create_data_dir(main_urls_and_dirs):
    if not os.path.exists(dataPath):
        os.mkdir(dataPath)

    for url, path in main_urls_and_dirs.items():
        for dir_ in path:
            if dir_ and not os.path.exists(dir_):
                os.mkdir(dir_)


# function creates all necessary urls based on category
# category which was chose with app args
def get_main_urls_and_dirs(args):
    main_urls = {}

    for rentaltype in args.rentaltype:
        for propertytype in args.propertytype:
            for city in args.city:
                main_url = ParseResult(scheme='https', netloc=hostURL,
                                        path=(f'{typesPL.get(rentaltype)}/'+
                                            f'{typesPL.get(propertytype)}/'+
                                            f'{city.lower()}/'), params='',
                                        query=(f'nrAdsPerPage={offersPerPage}'),
                                        fragment='').geturl()
                json_path = f'{dataPath}\{rentaltype}-{propertytype}-{city.lower()}'
                img_path = f'{json_path}\img' if args.image else ''
                main_urls[main_url] = (json_path, img_path)
    return main_urls


def main():
    try:
        args = get_args()
        print(f'So, you are looking for {"/".join(args.rentaltype)}', 
            f'{"/".join(args.propertytype)} in {("/".join(args.city)).lower()}...')

        main_urls_and_dirs = get_main_urls_and_dirs(args)
        create_data_dir(main_urls_and_dirs)
        print('All necessary directories have been created.')

        proceed(main_urls_and_dirs)
    except Exception as error:
        print('Houston, we have a problem:\n\t\t', str(error).upper())


if __name__ == "__main__":
    main()