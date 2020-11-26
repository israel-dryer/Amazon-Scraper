
# Build an Amazon Webscraper
The goal of this project is to build a webscraper that extracts product search results from www.amazon.com. This project is designed to give a beginner or intermediate programmer some experience with webscraping in a practical application. 

## Prerequisites
Some basic working knowledge of [Selenium]() and [BeautifulSoup]() is assumed by the lesson content. Additionally, you will need to have installed the related Python libraries as well as the webdriver of your choice. I will provide instructions with Microsoft Edge in mind, however, I will highlight the few differences that exists for Firefox or Chrome browsers so that you can follow along with any of those webdrivers.

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
There are a few ways to conduct a product search. The first is to automate the browser by finding the input element, insert the search text, and sending a RETURN key command to the browser to submit the command. However, this kind of automation, while fun to write, is unnecessarily and create potential for program failure. You should only automate with the webdriver when absolutely necessary when webscraping, especially because it's the slowest method for scraping data. Instead, type in a search term into the browser, and then press the enter key. You'll notice that the search term has been embedded into the url of the site. We can use this information to create a function that will build the necessary url for our driver to retrieve. This will be much more efficient in the long term, and less prone to program failure.

The search url for an "ultrawide monitor" looks like this: 
```
https://www.amazon.com/s?k=ultrawide+monitor&ref=nb_sb_noss_2
```
So, in order to generate this url for any search term, we need to replace any spaces in the search term with a "+" and insert it into the middle of this url with string formatting. So, let's define a function to do just that.

```python
def get_url(search_text):
    """Generate a url from search text"""
    template = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_1'
    search_term = search_text.replace(' ', '+')
    return template.format(search_term)
```
We now have a function that will generate a url based on the search text that we provide. Now, try again.

```python
url = get_url('ultrawide monitor')
driver.get(url)
```
This should produce the same results as before.. navigating to the ultrawide monitor search results. Try it again with a different search term if you wish.

## Survey page content and structure
The next thing to do is to survey the page content and structure. I know that I want to extract data for each record, and all of the records appear to be in a fairly consistent structure. But, there are a few oddities that we'll need to deal with. First, I see there is sponsored results amongst we might consider actual results. Also, there are sections that are obviously ads. Finally, there are multiple pages of results, so we need to work out how to navigate to the next page and continue extracting results.

## Extract collection
Next, we are going to extract the content of this page from the html content in the background.  Before we do this, we'll need to create a **soup** object, which will parse the html content from the page content. Create a soup object using the `driver.page_content` to retrieve the html text, and then we'll use the default html parser to parse the html.

```python
soup = BeautifulSoup(driver.page_content, 'html.parser')
```
What I want to do first is try to identify something unique about a record that will enable me to extract all records from this page as a collection. So, the best way to do that is to use the document inspector. Right-click on the item you want to inspect, such as the heading, and click on "Inspect". On the right-hand side, or lower side of the browser, a document inspector will show the html content in the background. If you hover over an html element, it should highlight the element on the webpage so that you can see the element on the page related to the element you are hovering over in the code. What I'm looking for is the html tag that encloses the entire record, and if you look at what's being highlighted it's easier to spot when you've found it.

Once you've found the appropriate tag, you must find a way to identify it uniquely amongst all the other tags of it's name. A "div" tag is pretty generic, but often you can use a class, and id, or another property to identify it's group so that you can extract it. In this case, and "id" is a bit too specific. And, it appears that a class might be a bit too broad. You'll find out as you do this more and more that it's a bit more of an art than a science, so sometimes you'll have to try a few things before you find something that works. Given the available fields, it appears that the **class** `s-result-item` or the **data-component-type** with it's value of `s-search-result` would be good options to identify the record. Since the data component type appears to be a bit more specific than the class, I'm going to go ahead and use it instead.  Let's use the soup object we create previously to extract all elements with the data-component-type of "s-search-result".
```python
results = soup.find_all('div', {'data-component-type': 's-search-result'})
```
If we print the length of the results list, we'll see that it returns a bit more than the results supposedly returned from our search... The difference here is the additional sponsored content that is inserted into the search results. You can do the math... the amount of sponsored content is not insignificant... I've seen that it's around 30% roughly.

## Prototype the record
Now that we've identify the collection of records from the page, what we need to do now is prototype the extract of a single record. After we've gotten that down, we can apply this model to the entire record set.
```python
# select a single record to build a prototype model
item = results[0]
```
Back to the webpage. The most obvious piece of information we'll need to extract is the record header, or description. If you right-click and select inspect, you'll be able to see the html code behind that. You may need to click inspect a few times to get to the level of detail you need. We can see immediately that his element is in several layers, and includes both a hyperlink and the text with the a tag that lies with the `h2` tag. It appears that the most easily identifiable tag here would be the `h2` tag. And since it's likely to be the only `h2` tag within this record, we can use a very simply property methodology to extract it. We'll traverse the tree using `h2`, and then a tag, saving this to the `atag` varible. Then, we can extract both the description and the url from the a tag... the description from the text... and the url by getting the `href` property. Though, we'll need to prepend the base amazon path to get the full url'
```python
atag = item.h2.a
description = atag.text.strip()
url = 'https://www.amazon.com' + atag.get('href')
```
The next item to get is the price. Right-click on the price to inspect it. As you can see, the price is also nested in several layers of tags. There appears to be tags containing the parts, as well as the entire text of the price. From what I can tell, we could potentially grab the `a-offscreen` class of the span tag here... but that might be a bit too generic a class. The safer, but more verbose path would be to get the `a-price` class first, and then grab the span underneath that with an `a-offscreen` class. We could also just grab the first span inside the `a-price` span, but that might not always be the element we want. But, we can get the text of this price as follows. We may decide to convert this to a float down the road, but for now this is just fine.

```python
price_parent = item.find('span', 'a-price')
price = price_parent.find('span', 'a-offscreen').text
```
The next two things that will be interesting are the rating out of 5, and the number of reviews.
Right-click on the stars and click inspect. If we dig in, it looks like we can easily identify this with the "i" tag. And, since there's unlikely to be another similar tag inside this record, we can access it simple through the tree navigation. And, we only want the text, so we can use the text property of the tag element.
```python
rating = item.i.text
```
Next, if we inspect the count of reviews, we can see that there isn't much to work with here, but, there is a 'dir' property that will allow us to access this item if we combine it with the class 'a-size-base' in order to make this as unique as possible.
```python
review_count = item.find('span', {'class': 'a-size-base', 'dir': 'auto'}).text
```
That is all that we're going to grab from each record for this exericise, But if there are additionally details that you'd want to grab, you can repeat the steps we've just gone through for each of those additional items.

## Generalize the pattern
Now that we've prototyped a method for a single record, it's now time to generalize that pattern within a function so that we can apply it to all the records on the page. Fortunately, we can copy and paste a lot of the code we've already written.

```python
def extract_record(item):
    """Extract and return data from a single record"""
    
    # description and url
    atag = item.h2.a
    description = atag.text.strip()
    url = 'https://www.amazon.com' + atag.get('href')
    
    # product price
    price_parent = item.find('span', 'a-price')
    price = price_parent.find('span', 'a-offscreen').text
    
    # rating and review count
    rating = item.i.text
    review_count = item.find('span', {'class': 'a-size-base', 'dir': 'auto'}).text
    
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
What is going to happen when we run this is that we are going to get some errors. The reason is that our model assumes that this information is available for each result. However, believe it or not, there are records without prices, without rankings, or ratings, etc... So, what we need to do is add some error handling to our code for these situations. If there's no price it means the item is not available. I don't care about these items, so I'm just going to return an empty record. However, if the review or rating is missing, I'll just set those as empty, but I'll still keep the record, since it's entirely possibly for a product to have not been reviewed.

```python
def extract_record(item):
    """Extract and return data from a single record"""
    
    # description and url
    atag = item.h2.a
    description = atag.text.strip()
    url = 'https://www.amazon.com' + atag.get('href')
    try:
        # product price
        price_parent = item.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text
    except AttributeError:
        return
    
    try:
        # rating and review count
        rating = item.i.text
        review_count = item.find('span', {'class': 'a-size-base', 'dir': 'auto'}).text
    except AttributeError:
        rating = ''
        review_count = ''
        
    result = (description, price, rating, review_count, url)
    
    return result
```
The only additional adjustment I need to make is to check that I don't try to append an empty record.
```python
records = []

results = soup.find_all('div', {'data-component-type': 's-search-result'})

for item in results:
    record = extract_record(item)
    if record:
        records.append(record)
```
## Getting the next page
The next step is to navigate to the next page. One way to get the next page is to find the button with the webdriver and click it. This does work. There is an easier way, and that is simply to extract the url from the button link. This will take us directly to the next page without having to resort to unnecessary automation. However, there is an even easier way, and I didn't notice it until I started preparing for this video, and that is simply to adjust the query in the url. If you click on the next button, you'll notice that there is a query parameter added to the url for page number. Any search that you do with amazon will result in a maximum of 20 pages of results. This means, that we can add this page query to the url, and using string formatting, request the next page until we've extracted from all 20 pages. To make this easier, we can modify our url generation function so that it includes the placeholder in the returned url. 

```python
def get_url(search_text):
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
Now that we have accounted for pagination with our url, and we have generalized the page data extraction, we can put this all together to scrape the search results for all 20 pages .

```python
import csv
from bs4 import BeautifulSoup
from msedge.selenium_tools import Edge, EdgeOptions


def get_url(search_text):
    """Generate a url from search text"""
    template = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_1'
    search_term = search_text.replace(' ', '+')
    
    # add term query to url
    url = template.format(search_term)
    
    # add page query placeholder
    url += '&page{}'
        
    return url

def extract_record(item):
    """Extract and return data from a single record"""
    
    # description and url
    atag = item.h2.a
    description = atag.text.strip()
    url = 'https://www.amazon.com' + atag.get('href')
    try:
        # product price
        price_parent = item.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text
    except AttributeError:
        return
    
    try:
        # rating and review count
        rating = item.i.text
        review_count = item.find('span', {'class': 'a-size-base', 'dir': 'auto'}).text
    except AttributeError:
        rating = ''
        review_count = ''
        
    result = (description, price, rating, review_count, url)
    
    return result

def main(search_term):
    """Run main program routine"""
    
    # startup the webdriver
    options = EdgeOptions()
    options.use_chromium = True
    driver = Edge(options=options)
    
    records = []
    url = get_url(search_term)
    
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
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Description', 'Price', 'Rating', 'ReviewCount', 'Url'])
        writer.writerows(records)
        
 # run the main program
 main('ultrawide monitor')
```
