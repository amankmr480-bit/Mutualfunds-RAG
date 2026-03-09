# Phase 1: Data Acquisition & Scraping
from scraper.scraper import scrape_funds, scrape_and_save
from scraper.parser import REQUIRED_FIELDS

__all__ = ["scrape_funds", "scrape_and_save", "REQUIRED_FIELDS"]
