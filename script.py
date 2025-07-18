import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


# ANSI color codes
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def fetch_image_urls(query, num_images=10):
    headers = {"User-Agent": "Mozilla/5.0"}
    image_urls = set()
    offset = 0
    while len(image_urls) < num_images:
        search_url = f"https://www.bing.com/images/search?q={query.replace(' ', '+')}&form=HDRSC2&first={offset}"
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        found = 0
        for img_tag in soup.find_all("img"):
            src = img_tag.get("src")
            if src and src.startswith("http"):
                if src not in image_urls:
                    image_urls.add(src)
                    found += 1
            if len(image_urls) >= num_images:
                break
        if found == 0:
            break  # No more images found, exit loop
        offset += found
        time.sleep(1)  # Be polite and avoid hammering the server
    return list(image_urls)[:num_images]


def download_images(image_urls, folder):
    os.makedirs(folder, exist_ok=True)
    for idx, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=10)
            ext = os.path.splitext(urlparse(url).path)[1]
            if not ext or len(ext) > 5:
                ext = ".jpg"
            filename = os.path.join(folder, f"image_{idx+1}{ext}")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(
                f"{Colors.OKGREEN}✔ Downloaded:{Colors.ENDC} {Colors.OKCYAN}{filename}{Colors.ENDC}"
            )
        except Exception as e:
            print(
                f"{Colors.FAIL}✖ Failed to download {url}:{Colors.ENDC} {Colors.WARNING}{e}{Colors.ENDC}"
            )


if __name__ == "__main__":
    print(f"{Colors.HEADER}{Colors.BOLD}Image Scraper{Colors.ENDC}")
    topic = input(f"{Colors.OKBLUE}Enter topic to search images for:{Colors.ENDC} ")
    num_images_input = input(
        f"{Colors.OKBLUE}Enter number of images to download:{Colors.ENDC} "
    )
    num_images = int(num_images_input) if num_images_input.strip() else 10
    folder = f"output/images_{topic.replace(' ', '_')}"
    print(f"{Colors.OKCYAN}Fetching image URLs for '{topic}'...{Colors.ENDC}")
    image_urls = fetch_image_urls(topic, num_images=num_images)
    print(f"{Colors.OKCYAN}Downloading images to '{folder}'...{Colors.ENDC}")
    download_images(image_urls, folder)
    print(
        f"{Colors.OKGREEN}{Colors.BOLD}Downloaded {len(image_urls)} images to '{folder}'{Colors.ENDC}"
    )
