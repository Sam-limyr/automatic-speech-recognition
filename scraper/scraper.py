'''
References:
- https://wamiller0783.github.io/TED-scraping-post.html
- https://github.com/The-Gupta/TED-Scraper/blob/master/Scraper.ipynb
'''

from bs4 import BeautifulSoup, Comment
import json
import requests
import os
import re

from time import sleep
from random import randint

import pandas as pd

from dateutil import parser
import sys


TEST_URL = "https://www.ted.com/talks/abdallah_ewis_the_forgotten_queen_of_egypt"

DATA_STORAGE_ROOT = os.path.join(os.getcwd(), "scraper", "data")
AUDIO_DATA_STORAGE = os.path.join(DATA_STORAGE_ROOT, "audio")
TRANSCRIPT_DATA_STORAGE = os.path.join(DATA_STORAGE_ROOT, "transcript")


def get_page_data_from_url(url):
    """
    Scrapes data from a url, given the url. Uses the 'requests' module to fetch data.
    Specifically written to scrape data from the TEDTalks page (root: https://www.ted.com/talks)
    :param url: The url to scrape data from.
    :return: Returns the page data, as a string.
    """
    response = requests.get(url)

    if not response.ok:
        print(f"Error encountered while accessing url: <{url}>")
        return

    print(response.text)


def parse_page_data_from_text(page_text):
    """
    Obtains the audio and transcript of a page, given its page text.
    Specifically written to scrape data from the TEDTalks page (root: https://www.ted.com/talks)
    :param page_text:
    :return:
    """
    pass


def main():
    get_page_data_from_url(TEST_URL)


if __name__ == "__main__":
    main()
