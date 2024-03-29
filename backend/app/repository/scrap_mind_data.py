"""Scrape data from the Mind charity website."""
import os
import time
import uuid
from datetime import datetime
from typing import Annotated, Dict, List, Optional

import pandas as pd
from bs4 import BeautifulSoup
from requests_html import HTMLSession  # type: ignore
from logging import getLogger

logger = getLogger(__name__)

MIND_URL = "https://www.mind.org.uk"

URLS = {
    "conditions_and_drugs": [
        "https://www.mind.org.uk/information-support/types-of-mental-health-problems/",
        "https://www.mind.org.uk/information-support/drugs-and-treatments/",
    ],
    "helping_someone": [
        "/information-support/types-of-mental-health-problems/mental-health-problems-introduction/for-friends-family/",
        "/information-support/guides-to-support-and-services/seeking-help-for-a-mental-health-problem/helping-someone-else-seek-help/",
        "/information-support/helping-someone-else/carers-friends-family-coping-support/am-i-a-carer/",
        "/information-support/tips-for-everyday-living/student-life/for-friends-and-family/",
        "/information-support/tips-for-everyday-living/lgbtqia-mental-health/supporting-someone-who-is-lgbtqia/",
    ],
}

URLS_TO_DISCARD = [
    "https://www.mind.org.uk/information-support/types-of-mental-health-problems/depression/",
    "https://www.mind.org.uk/information-support/drugs-and-treatments/antidepressants-a-z/overview/",
    "https://www.mind.org.uk/information-support/types-of-mental-health-problems/recreational-drugs-alcohol-and-addiction/",
    "https://www.mind.org.uk/information-support/drugs-and-treatments/complementary-and-alternative-therapies/",
    "https://www.mind.org.uk/information-support/drugs-and-treatments/sleeping-pills-and-minor-tranquillisers-a-z/overview/",
    "https://www.mind.org.uk/information-support/drugs-and-treatments/antipsychotics-a-z/overview/",
]


class Scraper:
    """This class aims to scrape data from the "Types of mental health problems", "Drugs and treatments" and the sub-sections from the "Helping someone else" as they all share the same HTML structure."""

    session = HTMLSession()

    def __init__(self, urls_to_discard: Optional[List[str]] = None) -> None:
        """Initialise Mind data scraper.

        Args:
            urls_to_discard (List[str]): list of URLs to discard, it overrides pre-defined URLs for Mind.

        """
        if urls_to_discard is None:
            self.urls_to_discard = URLS_TO_DISCARD
        else:
            self.urls_to_discard = urls_to_discard

    def get_html_text(self, url: str) -> str:
        """Retrieve the HTML text content of a webpage.

        Args:
            url (str): The URL of the webpage.

        Returns:
            str: The HTML text content of the webpage.
        """
        return self.session.get(url).text  # type: ignore

    def create_soup(self, url: str) -> BeautifulSoup:
        """Create a BeautifulSoup object from the HTML text content of a webpage.

        Args:
            url (str): The URL of the webpage.

        Returns:
            BeautifulSoup: A BeautifulSoup object representing the webpage's HTML structure.
        """
        html_text = self.get_html_text(url)
        soup = BeautifulSoup(html_text, "lxml")

        return soup

    def build_subpage_url(self, sub_page_url: str) -> str:
        """Build a reachable URL for a subpage given its directory.

        Args:
            sub_page_url (str): The directory of the subpage.

        Returns:
            str: The complete URL for the subpage.
        """
        if sub_page_url.startswith(MIND_URL):  # Some links can be absolute
            return sub_page_url
        else:
            return str(MIND_URL + sub_page_url)

    def create_dataframe(self, data: Dict[str, Dict[str, str]]) -> pd.DataFrame:
        """Create a pandas DataFrame from the given data.

        Args:
            data (dict): A dictionary containing URL and TextScraped pairs.

        Returns:
            pd.DataFrame: The created DataFrame with columns TextScraped, TimeStamp, URL, and ArchivedURL.
                Index:
                    RangeIndex
                Columns:
                    Name: uuid, dtype: object
                    Name: html_scraped, dtype: object
                    Name: text_scraped, dtype: object
                    Name: timestamp, dtype: datetime64[ns]
                    Name: url, dtype: object
        """
        df = pd.DataFrame(data.values())

        df["timestamp"] = datetime.now()

        df["uuid"] = df.apply(lambda row: str(uuid.uuid4()), axis=1)

        df = df[
            ["uuid", "html_scraped", "text_scraped", "timestamp", "url"]
        ]  # Rearrange Columns

        return df

    def extract_section_list(self, url: str) -> Dict[str, str]:
        """Extracts a dictionary of object names and their corresponding sub-URLs.

        E.g. From the types of mental health problems page. We would expect a dictionary of {"Anger": "url_to_anger_page"}

        Args:
            url (str): the url of a section from the information and support page such "Types of mental health problems" page.

        Returns:
             Dict[str, str]: A dictionary where the keys are object names and the values are their sub-URLs.
        """
        soup = self.create_soup(url)

        objects: Dict[str, str] = {}
        for div in soup.find_all(
            "div", class_="content-area bg-white"
        ):  # Where the list starts
            for a_tag in div.find_all("a"):
                object_name = a_tag.get_text(strip=True)
                href = a_tag["href"]

                if (
                    object_name == "Yes"
                ):  # The class content-area bg-white contains some non related text such as the "Yes" section
                    return objects

                objects[object_name] = href

        return objects

    def get_object_side_bar_urls(
        self, url: str, side_bar_url_to_exclude: Optional[str] = None
    ) -> List[str]:
        """This function should return the side bar urls for each object found with the extract_section_list() function.

        Args:
            url (str): object's url. E.g. The URL to the anger condition page or URL to the Antidepressants page.
            side_bar_url_to_exclude (Optional[str]): sidebar url to exclude if needed. E.g. Antidepressants contains URL Antidepressants A–Z which is also an object on its own. Defaults to None.


        Returns:
            List[str]: A list of side bar urls of an object such as a condition or a drug.
        """
        side_bar_urls = []

        soup = self.create_soup(self.build_subpage_url(url))

        side_bar_list = soup.find("ul", class_="sidebar-menu")

        if side_bar_list:
            for li_tag in side_bar_list.find_all("li"):  # type: ignore
                a_tag = li_tag.find("a")
                href = a_tag["href"]
                side_bar_urls.append(href)

            if side_bar_url_to_exclude:
                side_bar_urls = [
                    url
                    for url in side_bar_urls
                    if not url.endswith(side_bar_url_to_exclude)
                ]
        else:
            # There's no sidebar, try an alternative layout
            # These are special cases for some index pages:
            # - Depression
            # - Recreational drugs
            # - Complementary and alternative therapies
            navigation_list = soup.find_all("div", class_="content-area")[1].find_all(
                ["h2", "h3"]
            )
            if navigation_list:
                for heading in navigation_list:
                    a_tag = heading.find("a")
                    if a_tag and "href" in a_tag.attrs:
                        side_bar_urls.append(a_tag["href"])

        return side_bar_urls

    def scrape_sub_page_data(
        self, sub_page_url: str, content_class: str
    ) -> Dict[str, str]:
        """This function scrapes data given a page URL and the class name of where contents are.

        Args:
            sub_page_url (str): The URL of the sub-page to scrape.
            content_class (str): The class name of the elements containing the desired content.

        Returns:
            Dict[str, str]: A dictionary that contains the url, raw HTML and scraped texts.
        """
        sub_page_data = []

        soup = self.create_soup(self.build_subpage_url(sub_page_url))

        # Contents for pages with a sidebar are stored in the col-md-8 class, and for pages without a sidebar, contents are stored in the col-md-12 class.
        content_divs = soup.find_all("div", class_=content_class)

        for div in content_divs:
            heading = div.find(["h2", "h3"])
            sub_page_texts = div.find_all(["p", "li"])

            if heading is not None:
                sub_page_data.append(heading.text)

            for sub_page_text in sub_page_texts:
                sub_page_data.append(sub_page_text.text)

        return {
            "url": self.build_subpage_url(sub_page_url),
            "html_scraped": "\n".join([str(div) for div in content_divs]),
            "text_scraped": "\n".join(sub_page_data),
        }

    def discard_decision(self, url: str) -> bool:
        """Decide whether a page should be discarded.

        Args:
            url (str): page url

        Returns:
            bool: discard decision
        """
        return url in self.urls_to_discard


def discard_non_content(
    scraper: Scraper, data: Dict[str, Dict[str, str]]
) -> Dict[str, Dict[str, str]]:
    """Discard pages that do not contain content.

    Args:
        scraper (Scraper): a scraper object.
        data (Dict[str, str]): empty or existing dataset.

    Returns:
        Dict[str, Dict[str, str]]: scraped data.
    """
    cleaned_data = {
        url: item for url, item in data.items() if not scraper.discard_decision(url)
    }
    return cleaned_data


def scrape_conditions_and_drugs_sections(
    scraper: Scraper, data: Dict[str, Dict[str, str]]
) -> Dict[str, Dict[str, str]]:
    """Scrapes data for the 'Types of mental health problems' and 'Drugs and treatments' sections.

    Args:
        scraper (Scraper): a scraper object.
        data (Dict[str, str]): empty or existing dataset.

    Returns:
        Dict[str, Dict[str, str]]: scraped data.
    """
    logger.info(
        "Scraping data from the 'Types of mental health problems' and 'Drugs and treatments' section"
    )

    for url in URLS["conditions_and_drugs"]:
        logger.info(f"\nScraping data from {url}\n")
        objects = scraper.extract_section_list(url)

        logger.info(f"Found {len(objects)} objects")

        for obj, obj_url in objects.items():
            logger.info(f"Scraping data for the {obj} object")
            sub_page_urls = scraper.get_object_side_bar_urls(obj_url, "a-z/")
            column_class = "col-md-8 column" if sub_page_urls else "col-md-12 column"

            if sub_page_urls:
                for sub_page_url in sub_page_urls:
                    sub_page_data = scraper.scrape_sub_page_data(
                        sub_page_url, column_class
                    )
                    full_url = scraper.build_subpage_url(sub_page_url)
                    data[full_url] = sub_page_data
            else:
                single_page_data = scraper.scrape_sub_page_data(obj_url, column_class)
                full_url = scraper.build_subpage_url(obj_url)
                data[full_url] = single_page_data

        logger.info("\nSleeping for 30 seconds to prevent bot detection.")
        time.sleep(30)

    logger.info(
        "\nFinised scraping data from the 'Types of mental health problems' and 'Drugs and treatments' section\n"
    )

    return data


def scrape_helping_someone_section(
    scraper: Scraper, data: Dict[str, Dict[str, str]]
) -> Dict[str, Dict[str, str]]:
    """Scrapes data for the 'Helping someone else' sections.

    Args:
        scraper (Scraper): a scraper object.
        data (Dict[str, Dict[str, str]]): empty or existing dataset.

    Returns:
        Dict[str, Dict[str, str]]: scraped data.
    """
    logger.info("Scraping data from the 'Helping someone else' section\n")

    for url in URLS["helping_someone"]:
        logger.info(f"Scraping data from {url}")
        sub_page_urls = scraper.get_object_side_bar_urls(url, "a-z/")

        column_class = "col-md-8 column" if sub_page_urls else "col-md-12 column"

        if sub_page_urls:
            for sub_page_url in sub_page_urls:
                sub_page_data = scraper.scrape_sub_page_data(sub_page_url, column_class)
                full_url = scraper.build_subpage_url(sub_page_url)
                data[full_url] = sub_page_data
        else:
            single_page_data = scraper.scrape_sub_page_data(url, column_class)
            full_url = scraper.build_subpage_url(url)
            data[full_url] = single_page_data

    logger.info("\nFinished scraping data from the 'Helping someone else' section\n")

    return data

def scrape_mind_data() -> Annotated[pd.DataFrame, "output_mind_data"]:
    """Scrape data from Mind.

    Returns:
        pd.DataFrame: data scraped.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: text_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
    """
    scraper = Scraper()
    data: Dict[str, Dict[str, str]] = {}

    data = scrape_conditions_and_drugs_sections(scraper, data)
    data = scrape_helping_someone_section(scraper, data)
    data = discard_non_content(scraper, data)

    logger.info("Finished scraping data for all sections\n")

    logger.info(f"Creating dataframe with {len(data)} rows of data")
    df = scraper.create_dataframe(data)
    return df