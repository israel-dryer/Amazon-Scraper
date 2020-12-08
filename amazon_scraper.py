"""
    Amazon Web scraper

    Modified:   2020-12-07
    Author:     Israel Dryer
"""
import csv
from datetime import datetime
from time import sleep
from random import random
from typing import List, Tuple
from selenium.webdriver.remote import webelement, webdriver
from selenium.common.exceptions import NoSuchElementException
from msedge.selenium_tools import Edge, EdgeOptions


def save_data_to_csv(data: List[Tuple], filename: str, header: List[str]) -> None:
    """Save data to file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


def create_webdriver() -> webdriver:
    """Create and return an Edge webdriver"""
    options = EdgeOptions()
    options.use_chromium = True
    options.headless = True
    driver = Edge(options=options)
    return driver


def generate_url_template(search_term: str) -> str:
    """Generate the url based on the search term"""
    base_template = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_1'
    search_term = search_term.replace(' ', '+')
    stem = base_template.format(search_term)
    url_template = stem + '&page={}'
    return url_template


def extract_card_data(item: webelement) -> Tuple or None:
    """Extract data from a single record"""
    description = item.find_element_by_xpath('.//h2/a').text.strip()
    url = item.find_element_by_xpath('.//h2/a').get_attribute('href')
    try:
        price = item.find_element_by_xpath('.//span[@class="a-price"]//span[@class="a-offscreen"]').text
    except NoSuchElementException:
        return
    try:
        rating = item.find_element_by_tag_name('i').text
    except NoSuchElementException:
        rating = ""
    try:
        review_count = item.find_element_by_xpath('.//span[@class="a-size-base" and @dir="auto"]').text
    except NoSuchElementException:
        review_count = ""
    return description, price, rating, review_count, url


def run(search_term: str) -> None:
    """Run the Amazon webscraper"""
    records = []
    driver = create_webdriver()
    url_template = generate_url_template(search_term)

    for page in range(1, 21):  # Max of 20 pages of results can be scraped
        url = url_template.format(page)
        print(f"Extracting from: {url}")
        driver.get(url)
        sleep(0.5)
        cards = driver.find_elements_by_xpath('//div[@data-component-type="s-search-result"]')
        for card in cards:
            result = extract_card_data(card)
            if result:
                records.append(result)
        sleep(random() * 3)  # random delay to prevent blocking

    # shut down the web driver
    driver.quit()

    # save the data
    header = ['description', 'price', 'rating', 'review_count', 'url']
    filename = search_term.replace(' ', '_') + '_' + datetime.today().strftime('%Y%m%d') + '.csv'
    save_data_to_csv(records, filename, header)

    # notification
    print(f"Scraped {len(records):,d} for the search term: {search_term}")


if __name__ == '__main__':
    run('dell laptop')
