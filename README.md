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

    Scrapper creates \data directory and its subdirectories. Subdirectory name depends on the user input parameters (e.g. \data\renting-flat-poznan).

    Scraper downloads all pages from the category, goes through all pages, gets a single offer and then gets inside to mine info. 
    Then it goes to another offer.
    Page by page.
    Category by category.

    If otodom.pl block the query for pages, then scrapper will append this query to the end, to try it later.
    
    Scrapper saves offers info in JSON format files in \data subdirectories.
