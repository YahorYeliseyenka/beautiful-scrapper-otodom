# Install packages
```console
    pip3 install -r requirements.txt
```
# Run scrapper
    
## Required arguments:
  
    -rt --rentaltype    - Enter one or more rental type:
                                renting     - na wynajem
                                selling     - na sprzedaż
    -p  --propertytype  - Enter one or more property types: 
                                house       - domy
                                flat        - mieszkania
                                room        - pokoje
                                plot        - działki
                                premises    - lokale użytkowe
                                hall        - hale i magazyny
                                garage      - garaży
    -c  --city          - Enter one or more city names

    -sp --savephotos    - Use, if you want to save photos
    
## Optional arguments:

    -h, --help          - Show this help message and exit

## Example: 
```console
    py main.py -rt renting -pt flat room -c poznan
```
# Data arguments
    Url
    Offer name
    Offer description
    Photos
    Address
    Coordinates (Latitude, Longitude)
    Geo_level (Region, Sub-region, City, District)
    Characteristics (Space in m^2, Rooms num, Building type, Floor No and others)
    Prise (Value, Unit, Suffix)
    Features (Dishwasher, Fridge, Furniture, Oven, Stove, Washing machine, and others)
    Owner (Name, Type, Phones, Avatar)
    Extra (Advertiser type, Advert type, Agency)
    Creation date
    Last update date
# How it works

    Scrapper creates a '*\data' directory in the project folder. This 
    directory is used for storing the extracted data. Data is stored 
    in JSON files. The file names depend on the parameters entered 
    by the user. 
    E.g. '*\data\renting-flat-poznan.json'.

    Images are stored in the '*\data' subdirectories. Subdirectory names
    depend on the parameters entered by the user.
    E.g. '*\data\renting-flat-poznan-img\'.

    Scraper loads all pages from a category, views each page, gets 
    a single offer and then goes inside to collect data. 
    Then it goes to another offer.
    Page by page.
    Category by category.

    If otodom.pl blocks page downloading, then scrapper appends it to the end 
    of the queue, to try it later.
