import re
import random
import requests
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
from typing import Tuple
from collections import deque
from urllib.parse import urljoin, urlparse, unquote

WIKIPEDIA_HEADERS = {"User-Agent": "WikiRecommender/0.1 (https://github.com/letamquang-ai/Wiki_recommend.git)"}


def wikipedia_scrapper_single_page(url: str) -> Tuple[str, str]:
    # Scrape and process the given URL
    response = requests.get(url, headers=WIKIPEDIA_HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the URL: {url} with status code {response.status_code}")
    
    # Extract the text from the <div id="mw-content-text">
    parsed = BeautifulSoup(response.text, 'html.parser')
    resolved_link = parsed.find('link', rel='canonical')["href"]
    body_content = parsed.find('div', id='mw-content-text')
    if body_content is None:
        raise Exception(f"Could not find <div id='mw-content-text'> in the page: {url}")
    new_text = body_content.get_text(strip=True)

    return new_text, resolved_link


def wikipedia_scrapper(
    link: str,
    page_count: int = 20,
    *,
    verbose: bool = True,
    min_sleep_time: float = 0.25,
    max_sleep_time: float = 0.5
) -> pd.DataFrame:

    assert link.startswith(
        "https://en.wikipedia.org/wiki/"
    ), "Link must start with https://en.wikipedia.org/wiki/"

    result = []
    queue = deque([link])
    queued = {link}
    visited = set()

    with tqdm(
        total=page_count,
        desc="Scraping articles",
        disable=not verbose
    ) as pbar:

        while queue and len(result) < page_count:

            current_link = queue.popleft()

            if current_link in visited:
                continue

            try:
                response = requests.get(
                    current_link,
                    headers=WIKIPEDIA_HEADERS,
                    timeout=(10, 30),
                )
                response.raise_for_status()

            except requests.RequestException as error:
                if verbose:
                    print(f"Skipping {current_link}")
                    print(error)
                continue

            parsed = BeautifulSoup(response.text, "html.parser")

            canonical = parsed.find("link", rel="canonical")
            resolved_link = (
                canonical.get("href", current_link)
                if canonical else current_link
            )

            if resolved_link in visited:
                continue

            visited.add(resolved_link)

            body_content = parsed.find(
                "div",
                id="mw-content-text"
            )

            if body_content is None:
                continue

            # Extract the Wikipedia page title.
            path = urlparse(resolved_link).path
            title = (
                unquote(path[len("/wiki/"):])
                if path.startswith("/wiki/")
                else ""
            )

            # Only save actual articles, not Wikipedia namespace pages.
            if title and ":" not in title and "List_of" not in title:
                result.append({
                    "wikipedia_url": resolved_link,
                    "text": body_content.get_text(strip=True)
                })
                pbar.update(1)

            # Discover links using relative or absolute URLs.
            for anchor in body_content.find_all("a", href=True):

                href = anchor["href"]
                candidate = urljoin(resolved_link, href)
                parsed_url = urlparse(candidate)

                if parsed_url.netloc not in {
                    "en.wikipedia.org",
                    "www.en.wikipedia.org"
                }:
                    continue

                if not parsed_url.path.startswith("/wiki/"):
                    continue

                candidate_title = unquote(
                    parsed_url.path[len("/wiki/"):]
                )

                # Exclude Wikipedia namespaces and empty titles.
                if not candidate_title or ":" in candidate_title:
                    continue

                # Remove query strings and fragments.
                candidate = (
                    "https://en.wikipedia.org" + parsed_url.path
                )

                if candidate not in visited and candidate not in queued:
                    queue.append(candidate)
                    queued.add(candidate)

            sleep(
                (max_sleep_time - min_sleep_time)
                * random.random() + min_sleep_time
            )

    if len(result) < page_count:
        print(
            f"Warning: Requested {page_count} articles, "
            f"but only collected {len(result)}."
        )

    return pd.DataFrame(result)

