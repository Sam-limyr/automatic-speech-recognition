"""
References:
- https://wamiller0783.github.io/TED-scraping-post.html
- https://github.com/The-Gupta/TED-Scraper/blob/master/Scraper.ipynb
"""

from bs4 import BeautifulSoup
import json
import logging
import requests
import os
import re
from urllib import request

logger = logging.getLogger()
logging.basicConfig(level="INFO", format="%(levelname)s: %(filename)s: %(message)s")

TEST_URLS = [
    "https://www.ted.com/talks/ashley_whillans_3_rules_for_better_work_life_balance"
]

# Storage locations
DATA_STORAGE_ROOT = os.path.join(os.getcwd(), "scraper", "data")


# General constants
START_OF_TED_URL = "https://www.ted.com/talks/"


def scrape_data_from_url(url):
    """
    Attempts to scrape the audio file and transcript text from the given webpage.
    Specifically written to scrape data from the TEDTalks page (root: https://www.ted.com/talks).

    If either the audio file or the transcript does not exist, then this method will not scrape anything.
    Otherwise, the data will be saved to a folder marked by the url.
    :param url: The url to scrape data from.
    :return: No return value.
    """
    assert url.startswith(START_OF_TED_URL), f"Url provided does not start with expected url: <{url}>"
    saved_folder_name = url.replace(START_OF_TED_URL, "")
    saved_folder_path = os.path.join(DATA_STORAGE_ROOT, saved_folder_name)

    # Check if transcript exists, by attempting to access the page tab
    url = url + "/transcript"
    response = requests.get(url)
    if not response.ok:
        logger.warning(f"No transcript exists: <{url}>")
        return

    page_text = response.text
    transcript_text = get_page_transcript_text(page_text)
    if not transcript_text:
        return

    # Check if audio download exists
    audio_download_link = get_page_audio_download_link(page_text)
    if not audio_download_link:
        return

    # Save to file
    save_transcript_text(transcript_text, saved_folder_path)
    download_and_save_audio_file(audio_download_link, saved_folder_path)


# Audio constants
# Notice that the opening and closing parentheses are escaped
START_OF_METADATA = '<script data-spec="q">q\("talkPage.init",'
END_OF_METADATA = '\)</script>'
# Allow "." to match newlines using re.DOTALL
METADATA_REGEX_PATTERN = re.compile(f"{START_OF_METADATA}(.*?){END_OF_METADATA}", re.DOTALL)
METADATA_PATH_TO_AUDIO = ["__INITIAL_DATA__", "talks", 0, "downloads", "audioDownload"]
AUDIO_FILE_NAME = "audio.mp3"


def get_page_audio_download_link(page_text):
    """
    Obtains the audio data download link of a page, given its page text.
    Specifically written to scrape data from the TEDTalks page (root: https://www.ted.com/talks).

    Workflow:
    - Isolate and extract the audio download link from the page text using tag delimiters

    :param page_text: The raw page text from the website, as parsed by the requests module.
    :return: Returns the audio download link, or None if no link exists.
    """
    if not page_text:
        logger.error("No page text was passed to audio download link parser.")
        return None

    raw_metadata = METADATA_REGEX_PATTERN.search(page_text)
    if not raw_metadata:
        logger.warning("No metadata object was found.")
        return None

    json_metadata = json.loads(raw_metadata.group(1))

    # Locate the audio download link by traversing down the JSON object
    audio_metadata_url = json_metadata
    for key in METADATA_PATH_TO_AUDIO:
        try:
            # Note: This deliberately does not distinguish between accessing between:
            #           - a list, using an integer (e.g. 0)
            #           - a dict, using a key (e.g. "some_name").
            # This is because the metadata object combines both nested lists and nested dicts.
            audio_metadata_url = audio_metadata_url[key]
        except (KeyError, IndexError):
            logger.warning("The specified path to the audio download does not exist.")
            return None

    if not audio_metadata_url:
        logger.warning("No audio download link exists.")
        return None

    return audio_metadata_url


def download_and_save_audio_file(audio_download_url, path_to_save_to):
    """
    Downloads an audio file, given its url link. Saves the file to the required folder.
    :param audio_download_url: The url to download the audio from.
    :param path_to_save_to: The folder name to save this file to.
    :return: No return value.
    """
    if not os.path.isdir(path_to_save_to):
        os.mkdir(path_to_save_to)

    audio_file_saved_location = os.path.join(path_to_save_to, AUDIO_FILE_NAME)
    _, _ = request.urlretrieve(audio_download_url, filename=audio_file_saved_location)
    logger.info("Audio file saved.")


# Transcript constants
START_OF_TRANSCRIPT = "<!-- Transcript text -->"
END_OF_TRANSCRIPT = "<!-- /Transcript text -->"
# Allow "." to match newlines using re.DOTALL
TRANSCRIPT_REGEX_PATTERN = re.compile(f"{START_OF_TRANSCRIPT}(.*?){END_OF_TRANSCRIPT}", re.DOTALL)
TRANSCRIPT_TEXT_PARAGRAPH_TAG = "p"
TRANSCRIPT_FILE_NAME = "transcript.txt"


def get_page_transcript_text(page_text):
    """
    Obtains the speech transcript of a page, given its page text.
    Specifically written to scrape data from the TEDTalks page (root: https://www.ted.com/talks).

    Workflow:
    - Isolate and extract the transcript from the page text using the front and back comment delimiters.
    - Use BeautifulSoup to tidy up the transcript by removing unnecessary HTML tags.

    :param page_text: The raw page text from the website, as parsed by the requests module.
    :return: Returns the transcript text, or None if the text does not exist.
    """
    if not page_text:
        logger.error("No page text was passed to transcript parser.")
        return None

    raw_transcript = TRANSCRIPT_REGEX_PATTERN.search(page_text)
    if not raw_transcript:
        logger.warning("No transcript was found.")
        return None

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


def save_transcript_text(transcript_text, path_to_save_to):
    """
    Saves the transcript text to the required folder as a file.
    :param transcript_text: The text to write to file.
    :param path_to_save_to: The folder name to save this file to.
    :return: No return value.
    """
    if not os.path.isdir(path_to_save_to):
        os.mkdir(path_to_save_to)

    transcript_file_saved_location = os.path.join(path_to_save_to, TRANSCRIPT_FILE_NAME)
    with open(transcript_file_saved_location, "w") as file:
        file.writelines(transcript_text)
        logger.info("Transcript text saved.")


def main():
    if not os.path.isdir(DATA_STORAGE_ROOT):
        os.mkdir(DATA_STORAGE_ROOT)

    for url in TEST_URLS:
        logger.info(f"Scraping from url: <{url}>")
        scrape_data_from_url(url)


if __name__ == "__main__":
    main()
