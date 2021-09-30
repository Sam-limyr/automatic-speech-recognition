"""
References:
- https://wamiller0783.github.io/TED-scraping-post.html
- https://github.com/The-Gupta/TED-Scraper/blob/master/Scraper.ipynb
"""

from bs4 import BeautifulSoup
import requests
import os
import re


TEST_URL = "https://www.ted.com/talks/abdallah_ewis_the_forgotten_queen_of_egypt"

# Storage locations
DATA_STORAGE_ROOT = os.path.join(os.getcwd(), "scraper", "data")
AUDIO_DATA_STORAGE = os.path.join(DATA_STORAGE_ROOT, "audio")
TRANSCRIPT_DATA_STORAGE = os.path.join(DATA_STORAGE_ROOT, "transcript")

# Scraper constants
START_OF_TRANSCRIPT = "<!-- Transcript text -->"
END_OF_TRANSCRIPT = "<!-- /Transcript text -->"
# Allow "." to match newlines using re.DOTALL
TRANSCRIPT_REGEX_PATTERN = re.compile(f"{START_OF_TRANSCRIPT}(.*?){END_OF_TRANSCRIPT}", re.DOTALL)

TRANSCRIPT_TEXT_PARAGRAPH_TAG = "p"
TRANSCRIPT_TEXT_PARAGRAPH_PATTERN = re.compile(f"<{TRANSCRIPT_TEXT_PARAGRAPH_TAG}>(.*?)"
                                               f"</{TRANSCRIPT_TEXT_PARAGRAPH_TAG}>", re.DOTALL)


def get_page_data_from_url(url):
    """
    Scrapes data from a url, given the url. Uses the 'requests' module to fetch data.
    Specifically written to scrape data from the TEDTalks page (root: https://www.ted.com/talks)
    :param url: The url to scrape data from.
    :return: Returns the page data, as a string.
    """
    # Locate the transcript tab of the page
    url = url + "/transcript"

    response = requests.get(url)
    if not response.ok:
        print(f"Error encountered while accessing url: <{url}>")
        return

    return response.text


def parse_page_data_from_text(page_text):
    """
    Obtains the audio and transcript of a page, given its page text.
    Specifically written to scrape data from the TEDTalks page (root: https://www.ted.com/talks)

    Workflow:
    - Isolate and extract the transcript from the page text using the front and back comment delimiters
    - Use BeautifulSoup to tidy up the transcript by removing unnecessary HTML tags

    :param page_text:
    :return:
    """
    raw_transcript = TRANSCRIPT_REGEX_PATTERN.search(page_text)
    if not raw_transcript:
        print("No transcript was found.")
        return

    page_soup = BeautifulSoup(raw_transcript.group(1), "html.parser")

    # Extract transcript elements using the 'p' tag
    transcript_paragraphs = page_soup.find_all(TRANSCRIPT_TEXT_PARAGRAPH_TAG)

    # Basic data cleaning
    transcript = []
    for paragraph in transcript_paragraphs:
        paragraph = str(paragraph)

        # Remove the 'p' tags at the start and end
        paragraph = paragraph.replace(f"<{TRANSCRIPT_TEXT_PARAGRAPH_TAG}>", "")
        paragraph = paragraph.replace(f"</{TRANSCRIPT_TEXT_PARAGRAPH_TAG}>", "")

        # Remove excess spaces
        paragraph = re.sub("\\s+", " ", paragraph).strip()

        transcript.append(paragraph)

    return " ".join(transcript)


def main():
    page_text = get_page_data_from_url(TEST_URL)
    print(parse_page_data_from_text(page_text))


if __name__ == "__main__":
    main()
