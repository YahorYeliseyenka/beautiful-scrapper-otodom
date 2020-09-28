# Install packages
```console
    pip3 install -r requirements.txt
```
# Run scrapper
    
## Required arguments:
  
    -rt --rentaltype    - Enter one or more rental type:
                                renting     - na wynajem
                                selling     - na sprzedaż
    -p --propertytype   - Enter one or more property types: 
                                house       - domy
                                flat        - mieszkania
                                room        - pokoje
                                plot        - działki
                                premises    - lokale użytkowe
                                hall        - hale i magazyny
                                garage      - garaży
    -c --city           - Enter one or more city names
    
## Optional arguments:

    -h, --help          - Show this help message and exit

## Example: 
```console
    py main.py -rt renting -pt flat room -c poznan
```
# How it works

    Scrapper creates a '*\data' directory in the project folder. This 
    directory is used for storing the extracted data. Data is stored 
    in JSON files. The file names depend on the parameters entered 
    by the user (for example, '*\data\renting-flat-poznan.json').

    Scraper loads all pages from a category, views each page, gets 
    a single offer and then goes inside to collect data. 
    Then it goes to another offer.
    Page by page.
    Category by category.

    If otodom.pl blocks page downloading, then scrapper appends it to the end 
    of the queue, to try it later.s
