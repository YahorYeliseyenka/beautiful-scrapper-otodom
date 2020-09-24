import os
import traceback

import argparse
from urllib.parse import ParseResult

from scrapper import proceed, offersPerPage

dataPath = f'{os.getcwd()}\data'        # path for data in working dir
hostURL = 'www.otodom.pl'               # otodom.pl domain
typesPL = {'renting': 'wynajem',
            'selling': 'sprzedaz',
            'house': 'dom',
            'flat': 'mieszkanie',
            'room': 'pokoj',
            'plot': 'dzialka',
            'premises': 'lokal',
            'hall': 'haleimagazyny',
            'garage': 'garaz'}          # dict with path variables


# setup argumet parser with 4 arguments: propertytype, rentaltype, city
def get_args():
    parser = argparse.ArgumentParser(description='Provide input scrapper args')
    parser.add_argument('-rt', '--rentaltype', nargs='+', required=True,
                        help='Enter whether you are interested in *renting* or *selling*',
                        type=lambda input: is_valid(parser, ("renting", "selling"), input))
    parser.add_argument('-pt', '--propertytype', nargs='+', required=True,
                        help='Enter whether you are interested in a *house*, *flat*, *room*, *plot*, *premises*, *hall* or *garage*',
                        type=lambda input: is_valid(parser, ('house', 'flat', 'room', 'plot', 'premises', 'hall', 'garage'), input))
    parser.add_argument('-c', '--city', nargs='+', required=True,
                        help='Enter the city you are interested in')
    return parser.parse_args()


# check if arguments passed from console arr correct
def is_valid(parser, choices, input):
    return input if input in choices else parser.error("Args doesn't equal to {}".format(choices))


# create project data dirs for scrapper results
def create_dirs(urls_dirs):
    if not os.path.exists(dataPath):
        os.mkdir(dataPath)

    for ulr, dir_ in urls_dirs.items():
        if not os.path.exists(dir_):
            os.mkdir(dir_)


# create all necessary urls and dirs based on categories
# return dictionary {page_url : path_to_saving_data}
def get_urls_dirs(args):
    urls_data = {}

    for rentaltype in args.rentaltype:
        for propertytype in args.propertytype:
            for city in args.city:
                if rentaltype == 'selling' and propertytype == 'room': 
                    print(f'Ha-ha, rooms for sale, you\'re funny.')
                    continue
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
        # get arguments from argument parser
        args = get_args()

        # generate urls and dirs based on arguments
        urls_dirs = get_urls_dirs(args)

        # create all necessary dirs for data scrapping process
        create_dirs(urls_dirs)

        # run the scrapper
        proceed(urls_dirs)
    except Exception:
        print('Houston, we have a problem')
        traceback.print_exc()


if __name__ == "__main__":
    main()