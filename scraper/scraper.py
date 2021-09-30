"""
References:
- https://wamiller0783.github.io/TED-scraping-post.html
- https://github.com/The-Gupta/TED-Scraper/blob/master/Scraper.ipynb
"""

from bs4 import BeautifulSoup
import json
import requests
import os
import re
from urllib import request


TEST_URL = "https://www.ted.com/talks/ashley_whillans_3_rules_for_better_work_life_balance"

# Storage locations
DATA_STORAGE_ROOT = os.path.join(os.getcwd(), "scraper", "data")
AUDIO_DATA_STORAGE = os.path.join(DATA_STORAGE_ROOT, "audio")
TRANSCRIPT_DATA_STORAGE = os.path.join(DATA_STORAGE_ROOT, "transcript")
PLACEHOLDER_FILE_NAME = "placeholder"


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
        print(f"No transcript exists: <{url}>")
        return None

    return response.text


# Audio constants
# Notice that the opening and closing parentheses are escaped
START_OF_METADATA = '<script data-spec="q">q\("talkPage.init",'
END_OF_METADATA = '\)</script>'
# Allow "." to match newlines using re.DOTALL
METADATA_REGEX_PATTERN = re.compile(f"{START_OF_METADATA}(.*?){END_OF_METADATA}", re.DOTALL)
METADATA_PATH_TO_AUDIO = ["__INITIAL_DATA__", "talks", 0, "downloads", "audioDownload"]
AUDIO_FILE_EXTENSION = ".mp3"


def parse_audio_from_page_text(page_text):
    """
    Obtains the audio data of a page, given its page text.
    Specifically written to scrape data from the TEDTalks page (root: https://www.ted.com/talks)

    Workflow:
    - Isolate and extract the audio download link from the page text using tag delimiters
    - Call a download request to the audio download link to obtain the audio

    :param page_text: The raw page text from the website, as parsed by the requests module.
    :return: No return value, but will save the audio file to the path in AUDIO_DATA_STORAGE.
    """
    if not page_text:
        print("No page text was passed to audio parser.")
        return

    raw_metadata = METADATA_REGEX_PATTERN.search(page_text)
    if not raw_metadata:
        print("No metadata object was found.")
        return

    json_metadata = json.loads(raw_metadata.group(1))

    # Locate the audio download link by traversing down the JSON object
    audio_metadata_url = json_metadata
    for key in METADATA_PATH_TO_AUDIO:
        try:
            # Note: This deliberately does not distinguish between accessing between:
            #           - a list, using an integer (e.g. 0)
            #           - a dict, using a key.
            # This is because the metadata object combines both nested lists and nested dicts.
            audio_metadata_url = audio_metadata_url[key]
        except (KeyError, IndexError):
            print("The specified path to the audio download does not exist.")
            return

    if not audio_metadata_url:
        print("No audio download link exists.")
        return

    audio_file_saved_location = os.path.join(AUDIO_DATA_STORAGE, PLACEHOLDER_FILE_NAME + AUDIO_FILE_EXTENSION)
    _, _ = request.urlretrieve(audio_metadata_url, filename=audio_file_saved_location)
    print("Audio file saved.")


# Transcript constants
START_OF_TRANSCRIPT = "<!-- Transcript text -->"
END_OF_TRANSCRIPT = "<!-- /Transcript text -->"
# Allow "." to match newlines using re.DOTALL
TRANSCRIPT_REGEX_PATTERN = re.compile(f"{START_OF_TRANSCRIPT}(.*?){END_OF_TRANSCRIPT}", re.DOTALL)
TRANSCRIPT_TEXT_PARAGRAPH_TAG = "p"
TRANSCRIPT_FILE_EXTENSION = ".txt"


def parse_transcript_from_page_text(page_text):
    """
    Obtains the speech transcript of a page, given its page text.
    Specifically written to scrape data from the TEDTalks page (root: https://www.ted.com/talks)

    Workflow:
    - Isolate and extract the transcript from the page text using the front and back comment delimiters
    - Use BeautifulSoup to tidy up the transcript by removing unnecessary HTML tags

    :param page_text: The raw page text from the website, as parsed by the requests module.
    :return: No return value, but will save the transcript to the path in TRANSCRIPT_DATA_STORAGE
    """
    if not page_text:
        print("No page text was passed to transcript parser.")
        return

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

    transcript = " ".join(transcript)
    transcript_file_saved_location = os.path.join(TRANSCRIPT_DATA_STORAGE,
                                                  PLACEHOLDER_FILE_NAME + TRANSCRIPT_FILE_EXTENSION)
    with open(transcript_file_saved_location, "w") as file:
        file.writelines(transcript)
        print("Transcript text saved.")


def main():
    page_text = get_page_data_from_url(TEST_URL)
    if page_text:
        parse_audio_from_page_text(page_text)
        parse_transcript_from_page_text(page_text)


if __name__ == "__main__":
    main()
