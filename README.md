
# Build an Amazon Webscraper
The goal of this project is to build a webscraper that extracts product search results from www.amazon.com

## Prerequisites
[Selenium]() and [BeautifulSoup]() 
Additionally, the related Python libraries as well as the webdriver of your choice need to be installed.

## Startup the Webdriver
To begin, import the required project libraries
```python
import csv
from bs4 import BeautifulSoup

# for Firefox and Google Chrome
from selenium import webdriver

# for Microsoft Edge
from msedge.selenium_tools import Edge, EdgeOptions
```
Initialize an instance of the webdriver.
```python
# Firefox
driver = webdriver.Firefox()

# Google Chrome
driver = webdriver.Chrome()

# Microsoft Edge
options = EdgeOptions()
options.use_chromium = True
driver = Edge(options=options)
```
Now that the webdriver has started, navigate to amazon's website.

```python
url = 'https://www.amazon.com'
driver.get(url)
```
## Perform a product search
type in a search words into the amazon search bar, and then press the enter key. You'll notice that the search term has been embedded into the url of the site. We can use this information to create a function that will build the necessary url for our driver to retrieve.

The search url for an "iphone 14" looks like this: 
```
https://www.amazon.com/s?k=iphone+14&ref=nb_sb_noss_2
```
So, in order to generate this url for any search term, we need to replace any spaces in the search term with a "+" and insert it into the middle of this url with string formatting. So, let's define a function to do just that.

```python
def get_url(search_word):
    """Generate a url from search text"""
    template = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_1'
    search_term = search_word.replace(' ', '+')
    return template.format(search_term)
```
We now have a function that will generate a url based on the search text that we provide. Now, try again.

```python
url = get_url('iphone 14')
driver.get(url)
```
This should produce the same results as before.. navigating to the iphone 14 search results. Try it again with a different search term if you wish.

## Extract collection
Next, we are going to extract the content of this page from the html content in the background.  Before we do this, we'll need to create a **soup** object, which will parse the html content from the page content. Create a soup object using the `driver.page_content` to retrieve the html text, and then we'll use the default html parser to parse the html.

```python
soup = BeautifulSoup(driver.page_source, 'html.parser')
```
Right-click on the item you want to inspect, such as the heading, and click on "Inspect". On the right-hand side, or lower side of the browser, a document inspector will show the html content in the background. If you hover over an html element, it should highlight the element on the webpage so that you can see the element on the page related to the element you are hovering over in the code.

Once you've found the appropriate tag, you must find a way to identify it uniquely amongst all the other tags of it's name. A "div" tag is pretty generic, but often you can use a class, and id, or another property to identify it's group so that you can extract it. Given the available fields, it appears that the **class** `s-result-item` or the **data-component-type** with it's value of `s-search-result` would be good options to identify the record. Since the data component type appears to be a bit more specific than the class, Let's use the soup object we create previously to extract all elements with the data-component-type of "s-search-result".
```python
results = soup.find_all('div', {'data-component-type': 's-search-result'})
```
If we print the length of the results list, we'll see that it returns a bit more than the results supposedly returned from our search... The difference here is the additional sponsored content that is inserted into the search results.

## Prototype the record
Now that we've identify the collection of records from the page, what we need to do now is prototype the extract of a single record. After we've gotten that down, we can apply this model to the entire record set.
```python
# select a single record to build a prototype model
item = results[0]
```
Back to the webpage. The piece of information we'll need to extract is the record header, or description. If you right-click and select inspect, you'll be able to see the html code behind that. You may need to click inspect a few times to get to the level of detail you need. We can see immediately that his element is in several layers, and includes both a hyperlink and the text with the a tag that lies with the `h2` tag. It appears that the most easily identifiable tag here would be the `h2` tag. And since it's likely to be the only `h2` tag within this record, we can use a very simply property methodology to extract it. We'll traverse the tree using `h2`, and then a tag, saving this to the `atag` varible. Then, we can extract both the description and the url from the a tag... the description from the text... and the url by getting the `href` property. Though, we'll need to prepend the base amazon path to get the full url'
```python
atag = item.h2.a
description = atag.text.strip()
url = 'https://www.amazon.com' + atag.get('href')
```
The next item to get is the price. Right-click on the price to inspect it. As you can see, the price is also nested in several layers of tags. There appears to be tags containing the parts, as well as the entire text of the price. From what I can tell, we could potentially grab the `a-offscreen` class of the span tag here. 

```python
price = item.find('span', 'a-offscreen').text
```
The next two things that will be interesting are the rating out of 5, and the number of reviews.
Right-click on the stars and click inspect. we use span tag with class of `a-icon-alt` And, we only want the text, so we can use the text property of the tag element.

```python
rating = item.find('span', 'a-icon-alt').text
```
Next, if we inspect the count of reviews, the class `a-size-base s-underline-text` in order to make this as unique as possible.
```python
review_count = item.find('span', {'class': 'a-size-base s-underline-text'}).text
```
if there are additionally details that you'd want to grab, you can repeat the steps we've just gone through for each of those additional items.

## Generalize the pattern
Now that we've prototyped a method for a single record, it's now time to generalize that pattern within a function so that we can apply it to all the records on the page.

```python
def extract_record(item):
    """Extract and return data from a single record"""
    
    # description and url
    atag = item.h2.a
    description = atag.text.strip()
    url = 'https://www.amazon.com' + atag.get('href')
    
    # product price
    price = item.find('span', 'a-offscreen').text
    
    # rating and review count
    rating = item.find('span', 'a-icon-alt').text
    review_count = item.find('span', {'class': 'a-size-base s-underline-text'}).text
    
    result = (description, price, rating, review_count, url)
    
    return result
```
And then, we can apply that pattern to all records on the page.

```python
# create a list to store extracted records
records = []

# get all search results
results = soup.find_all('div', {'data-component-type': 's-search-result'})

# extract data from each results
for item in results:
    records.append(extract_record(item))
```
## Handling errors
What is going to happen when we run this is that we are going to get some errors. The reason is that our model assumes that this information is available for each result. However, believe it or not, there are records without prices, without rankings, or ratings, etc... So, what we need to do is add some error handling to our code for these situations. so we just going to return an empty record if the price, review or rating is missing.

```python
def extract_record(item):
    """Extract and return data from a single record"""
    
    # description and url
    atag = item.h2.a
    description = atag.text.strip()
    url = 'https://www.amazon.com' + atag.get('href')
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
        
    result = (description, price, rating, review_count, url)
    
    return result
```
The only additional adjustment we need to make is to check that we don't try to append an empty record.
```python
records = []

results = soup.find_all('div', {'data-component-type': 's-search-result'})

for item in results:
    record = extract_record(item)
    if record:
        records.append(record)
```
## Getting the next page
The next step is to navigate to the next page. we'll adjust the query in the url, If you click on the next button, you'll notice that there is a query parameter added to the url for page number. Any search that you do with amazon will result in a maximum of 20 pages of results. This means, that we can add this page query to the url, and using string formatting, request the next page until we've extracted from all 20 pages. To make this easier, we can modify our url generation function so that it includes the placeholder in the returned url. 

```python
def get_url(search_word):
    """Generate a url from search text"""
    template = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_1'
    search_term = search_text.replace(' ', '+')
    
    # add term query to url
    url = template.format(search_term)
    
    # add page query placeholder
    url += '&page={}'
        
    return url
```

## Putting it all together
Final script to scrape the search results for all 20 pages .

```python
import csv
from bs4 import BeautifulSoup
from selenium import webdriver

def get_url(search_word):
    """Generate a url from search text"""
    template = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_1'
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
    Product_url = 'https://www.amazon.com' + atag.get('href')
    
    
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
```
