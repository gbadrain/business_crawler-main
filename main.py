import argparse
import os
import re
import pandas as pd
from datetime import datetime
from ddgs import DDGS
from trafilatura import fetch_url, extract
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
from collections import defaultdict
import spacy
from typing import Dict, List, Any, Set

from config import (
    MAX_RESULTS_PER_QUERY,
    MIN_WORDS_FOR_CONTENT,
    OUTPUT_DIR,
    BLACKLIST_FILE,
)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extracts named entities from a given text using spaCy.

    Args:
        text (str): The input text from which to extract entities.

    Returns:
        Dict[str, List[str]]: A dictionary where keys are entity types (e.g., "PERSON", "ORG")
                               and values are lists of unique extracted entities of that type.
    """
    doc = nlp(text)
    entities: Dict[str, List[str]] = {
        "PERSON": [],
        "ORG": [],
        "GPE": [],
        "LOC": [],
        "PRODUCT": [],
        "EVENT": [],
        "DATE": [],
        "NORP": [],
        "FAC": [],
        "LAW": [],
        "LANGUAGE": [],
        "MONEY": [],
        "ORDINAL": [],
        "PERCENT": [],
        "QUANTITY": [],
        "CARDINAL": [],
        "WORK_OF_ART": [],
        "TIME": [],
        "LOC": [],
    }
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    return {k: list(set(v)) for k, v in entities.items() if v}


def search_links(query: str, max_results: int) -> List[Dict[str, str]]:
    """Performs a search using DuckDuckGo and returns a list of search results.

    Args:
        query (str): The search query.
        max_results (int): The maximum number of search results to return.

    Returns:
        List[Dict[str, str]]: A list of dictionaries, where each dictionary represents a search result
                               and contains 'href' (URL) and 'title'.
    """
    with DDGS() as ddgs:
        return [r for r in ddgs.text(query, max_results=max_results)]


def scrape_content(url: str, min_words: int = MIN_WORDS_FOR_CONTENT) -> str | None:
    """Scrapes the main content from a given URL, with a fallback mechanism.

    Args:
        url (str): The URL of the page to scrape.
        min_words (int): The minimum number of words required for the extracted content to be considered valid.

    Returns:
        str | None: The extracted main content as a string, or None if content could not be extracted
                      or did not meet the minimum word count.
    """
    downloaded = fetch_url(url)
    if downloaded:
        content = extract(downloaded, favor_recall=True, include_comments=True)
        if content and len(content.split()) >= min_words:
            return content

        soup = BeautifulSoup(downloaded, "html.parser")
        fallback_text = "\n".join(
            p.get_text() for p in soup.find_all("p") if p.get_text()
        )
        if fallback_text and len(fallback_text.split()) >= min_words:
            return fallback_text
    return None



def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be used as a safe filename.

    Replaces any character that is not an alphanumeric character or an underscore with an underscore.

    Args:
        name (str): The input string to sanitize.

    Returns:
        str: The sanitized string.
    """
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


def get_file_size_human_readable(file_path: str) -> str:
    """Converts a file size in bytes to a human-readable format (B, KB, MB).

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The file size in a human-readable format, or "N/A" if the file does not exist.
    """
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
    return "N/A"


def main() -> None:
    """Main function to run the Business Crawler.

    Parses command-line arguments, loads blacklist, performs searches,
    scrapes content, extracts entities, and saves results to CSV/JSON files.
    """
    parser = argparse.ArgumentParser(
        description="""Business Crawler: Automates web research by performing live searches, scraping content, extracting insights, and exporting structured data.

        Example usage:
            business-crawler "AI in healthcare" "Natural Language Processing"
            business-crawler "Quantum Computing" --max_results 5 --blacklist custom_blacklist.txt
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "queries",
        type=str,
        nargs="+",
        help="One or more search queries to perform (e.g., \"AI in healthcare\")."
    )
    parser.add_argument(
        "--max_results",
        type=int,
        default=MAX_RESULTS_PER_QUERY,
        help=f"Maximum number of search results to scrape per query (default: {MAX_RESULTS_PER_QUERY})."
    )
    parser.add_argument(
        "--blacklist",
        type=str,
        default=BLACKLIST_FILE,
        help=f"Path to a text file containing domains to skip during scraping, one domain per line (default: {BLACKLIST_FILE})."
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Load blacklist
    blacklist: Set[str] = set()
    if os.path.exists(args.blacklist):
        try:
            with open(args.blacklist, "r") as f:
                blacklist = {line.strip() for line in f if line.strip()}
            logging.info(f"Loaded {len(blacklist)} domains from {args.blacklist}")
        except IOError as e:
            logging.error(f"Error loading blacklist file {args.blacklist}: {e}")
    else:
        logging.info(
            f"Blacklist file not found at {args.blacklist}. Proceeding without a blacklist."
        )

    all_data: List[Dict[str, Any]] = []
    domain_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"success": 0, "fail": 0})

    for query in args.queries:
        logging.info(f"Searching for '{query}'...")
        try:
            search_results = search_links(query, args.max_results)
            if not search_results:
                logging.warning(f"No search results found for query: {query}")
                continue
        except Exception as e:
            logging.error(f"Error during search for '{query}': {e}")
            continue

        safe_name = sanitize_filename(query)
        output_path = f"{OUTPUT_DIR}/{safe_name}.csv"
        failed_log_path = f"{OUTPUT_DIR}/{safe_name}_failed.txt"

        query_data: List[Dict[str, Any]] = []
        failed_urls: List[str] = []

        from tqdm import tqdm
        for result in tqdm(search_results, desc=f"Scraping {query}"):
            url = result.get("href")
            title = result.get("title", "Untitled")
            domain = urlparse(url).netloc

            if domain in blacklist:
                logging.info(f"Skipping blacklisted domain: {url}")
                failed_urls.append(url)
                domain_stats[domain]["fail"] += 1
                continue

            logging.info(f"Scraping {url}...")
            try:
                content = scrape_content(url)
                if content:
                    snippet = content[:300].strip().replace("\n", " ") + "..."
                    scraped_at = datetime.utcnow().isoformat()

                    # Extract entities
                    entities = extract_entities(content)

                    query_data.append(
                        {
                            "topic": query,
                            "title": title,
                            "url": url,
                            "domain": domain,
                            "snippet": snippet,
                            "content": content,
                            "scraped_at": scraped_at,
                            "entities": entities,
                            "keywords": [],  # Placeholder for future keyword extraction
                        }
                    )
                    domain_stats[domain]["success"] += 1
                else:
                    logging.warning(f"No content could be scraped from {url}")
                    failed_urls.append(url)
                    domain_stats[domain]["fail"] += 1
            except Exception as e:
                logging.error(f"Error scraping {url}: {e}")
                failed_urls.append(url)
                domain_stats[domain]["fail"] += 1

        # Save per-topic output
        if query_data:
            df = pd.DataFrame(query_data)
            try:
                df.to_csv(output_path, index=False)
                logging.info(
                    f"Scraped data saved to {output_path} ({get_file_size_human_readable(output_path)})
                )
            except IOError as e:
                logging.error(f"Error saving data to {output_path}: {e}")
        else:
            logging.info(f"No content could be scraped for query: {query}")

        if failed_urls:
            try:
                with open(failed_log_path, "w") as f:
                    for url in failed_urls:
                        f.write(url + "\n")
                logging.warning(
                    f"Logged {len(failed_urls)} failed URLs to {failed_log_path}"
                )
            except IOError as e:
                logging.error(f"Error logging failed URLs to {failed_log_path}: {e}")

        all_data.extend(query_data)

    # Save aggregated CSV and JSON
    if all_data:
        df_all = pd.DataFrame(all_data)
        merged_csv = f"{OUTPUT_DIR}/_all_queries_merged.csv"
        merged_json = f"{OUTPUT_DIR}/_all_queries_merged.json"

        try:
            df_all.to_csv(merged_csv, index=False)
            df_all.to_json(merged_json, orient="records", indent=2)
            logging.info(
                f"All queries merged into {merged_csv} ({get_file_size_human_readable(merged_csv)}) and {merged_json} ({get_file_size_human_readable(merged_json)})
            )
        except IOError as e:
            logging.error(f"Error saving merged data: {e}")

    # Save domain success/failure log
    domain_log = f"{OUTPUT_DIR}/_domain_stats_summary.csv"
    try:
        pd.DataFrame(
            [
                {
                    "domain": domain,
                    "successes": stats["success"],
                    "failures": stats["fail"],
                }
                for domain, stats in sorted(
                    domain_stats.items(), key=lambda x: -x[1]["success"]
                )
            ]
        ).to_csv(domain_log, index=False)
        logging.info(f"Domain scraping summary saved to {domain_log}")
    except IOError as e:
        logging.error(f"Error saving domain summary: {e}")


if __name__ == "__main__":
    main()