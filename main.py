import os
import time

import argparse

DATA_PATH = f'{os.getcwd()}\data'


# setup argumet parser with 4 arguments: propertytype, rentaltype, city, image
def get_args():
    parser = argparse.ArgumentParser(description='Provide input scrapper args')
    parser.add_argument('-c', '--city', nargs='+', required=True,
                        help='Enter the city you are interested in')
    parser.add_argument('-rt', '--rentaltype', nargs='+', required=True, 
                        help='Enter whether you are interested in *renting* or *selling*',
                        type=lambda input: is_valid(parser, ("renting", "selling"), input))
    parser.add_argument('-pt', '--propertytype', nargs='+', required=True,
                        help='Enter whether you are interested in a *house* or *flat*',
                        type=lambda input: is_valid(parser, ('house', 'flat'), input))
    parser.add_argument('-i', '--image',
                        help='Enter smth if you are interested in image scrapping')
    return parser.parse_args()


# function checks if arguments passed from console arr correct
def is_valid(parser, choices, input):
    return input if input in choices else parser.error("Args doesn't equal to {}".format(choices))


def create_data_dir(args):
    if not os.path.exists(DATA_PATH): os.mkdir(DATA_PATH)

    for c in args.city:
        for rt in args.rentaltype:
            for pt in args.propertytype:
                json_path, img_path = (f'{DATA_PATH}\{c}-{rt}-{pt}', f'{DATA_PATH}\{c}-{rt}-{pt}\img')
                if not os.path.exists(json_path): os.mkdir(json_path)
                if not os.path.exists(img_path) and args.image: os.mkdir(img_path)


def main():
    args = get_args()
    print(f'It looks like you are interested in {"/".join(args.rentaltype)} {" or ".join(args.propertytype)} in {("/".join(args.city)).lower()}')
    create_data_dir(args)
    # print('So, you are looking for', args.)
    # print(f'{os.getcwd()}\data\{c}-{pt}-{rt}/img')


if __name__ == "__main__":
    main()