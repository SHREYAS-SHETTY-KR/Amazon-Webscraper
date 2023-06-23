''' Amazon Webscraper '''


import csv
from bs4 import BeautifulSoup
from selenium import webdriver

def get_url(search_word):
    """Generate a url from search text"""
    template = 'https://www.amazon.in/s?k={}&ref=nb_sb_noss_1'
    search_term = search_word.replace(' ', '+')
        
    # add search_term query to url
    url = template.format(search_term)
    
    # add page number query placeholder
    url += '&page={}'
    
    return url


def extract_record(item):
    """Extract and return data"""
    
    # description and url
    atag = item.h2.a
    description = atag.text.strip()
    Product_url = 'https://www.amazon.in' + atag.get('href')
    
    
    try:
        # product price
        price = item.find('span', 'a-offscreen').text
    except AttributeError:
        price = ''
     
    
    try:
        # rating and review count
        rating = item.find('span', 'a-icon-alt').text
        review_count = item.find('span', {'class': 'a-size-base s-underline-text'}).text
    except AttributeError:
        rating = ''
        review_count = ''
                
    result = (description, price, rating, review_count, Product_url)

    return result


def main(search_word):
    
    # startup the webdriver
    driver = webdriver.Chrome()
    
    records = []
    url = get_url(search_word)
    
    for page in range(1, 21):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        for item in results:
            record = extract_record(item)
            if record:
                records.append(record)
                
    driver.close()
    
    
    # save data to csv file
    with open('result.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Description', 'Price', 'Rating', 'ReviewCount', 'Url'])
        writer.writerows(records)
        
        
# run the main program
main('iphone 14')
