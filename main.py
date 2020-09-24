import os
import time

import argparse
from urllib.parse import ParseResult

from scrapper import proceed, offersPerPage

dataPath = f'{os.getcwd()}\data'
hostURL = 'www.otodom.pl'
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
    return parser.parse_args()


# function checks if arguments passed from console arr correct
def is_valid(parser, choices, input):
    return input if input in choices else parser.error("Args doesn't equal to {}".format(choices))


# function creates project data dirs for scrapper results
def create_dirs(urls_dirs):
    if not os.path.exists(dataPath):
        os.mkdir(dataPath)

    for ulr, dir_ in urls_dirs.items():
        if not os.path.exists(dir_):
            os.mkdir(dir_)


# function creates all necessary urls and dirs based on categories
# categories which were chose with app args
def get_urls_dirs(args):
    urls_data = {}

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
                urls_data[main_url] = json_path
    return urls_data


def main():
    try:
        args = get_args()

        print('Creating directories for saving data...')
        urls_dirs = get_urls_dirs(args)
        create_dirs(urls_dirs)

        print(f'Looking for {"/".join(args.rentaltype).upper()}', 
            f'{"/".join(args.propertytype).upper()} in {("/".join(args.city)).upper()} offers...')
        proceed(urls_dirs)
    except Exception as error:
        print('Houston, we have a problem:\n\t\t', str(error).upper())


if __name__ == "__main__":
    main()