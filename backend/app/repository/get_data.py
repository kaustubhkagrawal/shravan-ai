import os
from app.repository.scrap_mind_data import scrape_mind_data
from app.repository.scrap_nhs_data import scrape_nhs_data
from logging import Logger


def get_data() -> None:
    if not os.path.exists("data/mind.csv"):
        logger.info("Scraping data from Mind website")
        mind_csv = scrape_mind_data()
        mind_csv.to_csv("data/mind.csv", index=False)
    if not os.path.exists("data/nhs.csv"):
        logger.info("Scraping data from nhs website")
        nhs_csv = scrape_nhs_data()
        nhs_csv.to_csv("data/nhs.csv", index=False)

if __name__ == "__main__":
    logger = Logger("uvicorn")
    get_data()