from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urlparse, urljoin
from langdetect import detect_langs
from translate import Translator
import requests
import csv
import ollama  
import time
import geocoder

# Set to store internal URLs and count of total URLs visited
internal_urls = set()
total_urls_visited = 0

# Function to check if a URL is a valid one
def is_valid(url):
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    except ValueError as e:
        print(f"Error parsing URL: {url}. Error message: {e}")
        return False

# Function to get all links from a website based on provided keywords
def get_all_website_links(url, translated_words):
    global internal_urls
    urls = set()
    global session
    session = HTMLSession()
    try:
        response = session.get(url)
        response.html.render()
    except Exception as e:
        print("Error:", e)
        return urls
    if not response.html.raw_html:
        print(f"Empty content for URL {url}")
        return urls
    try:
        response = session.get(url)
        response.html.render()
    except ConnectionError or TimeoutError:
        pass
    soup = BeautifulSoup(response.html.html, "html.parser")
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href")
        if href is None or href == "":
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # Check if the URL is valid and belongs to the same domain
        if is_valid(href) and domain_name == parsed_href.netloc:
            for keyword in translated_words:
                if keyword in href:
                    if href not in internal_urls:
                        urls.add(href)
                        internal_urls.add(href)
    return urls

# Set to store processed URLs
processed_urls = set()

# Function to extract content from URLs and interact with ollama
def extract_url_content(internal_urls):
    global processed_urls
    for link in internal_urls:
        if link in processed_urls:
            continue
        else:
            processed_urls.add(link)
        try:
            response = session.get(link)
            response.html.render()
        except Exception as e:
            print("Error fetching URL content:", e)
            continue

        # Extract visible text content from the web page as text for parsing it to ollama
        soup = BeautifulSoup(response.html.raw_html, 'html.parser')
        text = soup.body.get_text()

        # Interact with ollama
        answer = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': f"{text} \
                    From this text I want you to extract ONLY the physical address. \
                    Do not return phone numbers, calendar dates, return only physical address. \
                    You WILL NOT SAY ANYTHING ELSE apart from the physical address. If you do not find any physical addresses \
                    in the text, YOU WILL PRINT: No physical address found! . \
                    So, extract from the text provided ONLY the address and nothing more. Do not say that \
                    you understand or anything at all, ONLY the address, and as I mentioned before if \
                    if you do not find any physical address in the text, YOU WILL PRINT No physical address found! .",
            },
        ])

        # Print the link and the extracted content
        print("-" * 100)
        print(link)
        print("-" * 100)
        print(answer['message']['content'])
        print("-" * 100)

        
        assistant_response = answer['message']['content']
        if ',' not in assistant_response or 'No physical address found!' in assistant_response:
            continue
        else:
            location = geocoder.arcgis(assistant_response)
            if location.ok:
                location.address
            else:
                location = "Location not found!"
            
        # Write the link and the extracted content to a txt file named output_locaitons
        with open("output_locations", "a") as output:
            output.write(f"{link} {location}\n")


# Set to store unique translated keywords to translated_words list
translated_words = set()

# Function to translate keywords based on the language of the webpage
def translate_keywords(url):
    global translated_words
    try:
        html = requests.get(url).content
        lang_co = BeautifulSoup(html, 'html.parser')
        lang = lang_co.html.get("lang")
        english_keywords = ("location", "about", "contact", "find")

        translator = Translator(to_lang=lang)

        # Translate each word in the list
        new_translations = {translator.translate(word) for word in english_keywords}
        translated_words.update(new_translations)
        return list(translated_words)
    except Exception as e:
        print("Translation Error:", e)
        # Returning translated_words as a list
        return []


# Recursive function to crawl through the website and extract links
# Adds the first link to the internal_url variable if any of the internal not found
def crawl(url, max_urls=30, processed_urls=set()):
    global total_urls_visited
    total_urls_visited += 1


    # Translate keywords for the current URL
    keywords = translate_keywords(url)
    # Get all links from the website

    links = get_all_website_links(url, keywords)
    new_links = links.difference(processed_urls)
    processed_urls.update(new_links)

    # Update internal URLs
    internal_urls.update(new_links)

    # If no new links are found, add the current URL to internal URLs
    if not new_links:  
        internal_urls.add(url)

    # Extract content from internal URLs
    extract_url_content(internal_urls)

    # Recursively crawl through new links
    for link in new_links:
        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls=max_urls,processed_urls=processed_urls)
    session.close()
    # Add the current URL to internal URLs if it's not already there
    if url not in internal_urls:
        internal_urls.add(url)

# Function to get links from a CSV file
def get_links_from_csv(file_path):

    #Returns a list of URLs from a CSV file.

    urls = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            urls.extend(row)
    return urls

# Main function runned in the terminal with the command:

if __name__ == "__main__":
    import argparse

    #Record the starting time
    start_time = time.time()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Link Extractor Tool with Python")
    parser.add_argument("csv_file", help="The CSV file containing the URLs to extract links from.")
    parser.add_argument("-m", "--max-urls", help="Number of max URLs to crawl, default is 30.", default=30, type=int)

    args = parser.parse_args()
    csv_file = args.csv_file
    max_urls = args.max_urls

    # Get URLs from CSV file
    urls = get_links_from_csv(csv_file)
    for url in urls:
        # Extract domain name from URL
        domain_name = urlparse(url).netloc
        crawl(url, max_urls=max_urls)
    
    end_time = time.time()  # Record the end time
    total_time_seconds = end_time - start_time

    # Convert total time to hours, minutes, and seconds
    total_time_hours = int(total_time_seconds // 3600)
    total_time_seconds %= 3600
    total_time_minutes = int(total_time_seconds // 60)
    total_time_seconds %= 60

    print("Total time spent:", total_time_hours, "hours,", total_time_minutes, "minutes, and", total_time_seconds, "seconds")