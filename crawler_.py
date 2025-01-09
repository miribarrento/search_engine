import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import whoosh
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
import os,os.path

# Define the schema for indexing(will be the infromation displayed when results show after sarch query)
schema = Schema(
    url=ID(stored=True),        # Unique identifier for the URL
    title=TEXT(stored=True),    # Title of the page
    content=TEXT(stored=True)                # Main content of the page
)

# Create or open an index directory
index_dir = "indexdir"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)

#create index
index = create_in(index_dir, schema)

#starting url
seed_url = "https://vm009.rz.uos.de/crawl/index.html"

#checks if the seed url and the url being crawled are in the same domain to prevent external links
def internal_link_checker(seed_url, link):
    full_url = urljoin(seed_url,link)
    seed_domain = urlparse(seed_url).netloc
    link_domain = urlparse(link).netloc

    return seed_domain == link_domain


#defines the main function,
def website_crawler_and_indexer(seed_url,visited_links = None):

    #if there are no links in visited_links then new list is initialized
    #this is to ensure that the list is not overwritten everytime the function is called
    if visited_links == None:
        visited_links = []

    #returns immideately if link has already been visited
    if seed_url in visited_links:
        return

    print(f"crawling:{seed_url}")
    visited_links.append(seed_url)

    try:
        #gets html content from url and saves it to content
        r = requests.get(seed_url)
        content = r.text

        #initializes soup object and creates parse trees
        soup = BeautifulSoup(content, "html.parser")

        #extracts title and body text for indexing purposes in schema
        title = soup.title.string if soup.title else "No Title"
        body_content = " ".join([p.get_text(strip=True) for p in soup.find_all("p")])

        #extracts all a tags with href attributes to get hyperlinks and prints them
        links = [a["href"] for a in soup.find_all("a", href=True)]

        #takes the extracted data and writes it using add_document to the index
        with index.writer() as writer:
            writer.add_document(
                url=seed_url,
                title=title,
                content=body_content
            )
        print(f"Indexed: {seed_url}")


        for link in links:
            full_url = urljoin(seed_url, link)  # Resolve the link
            if internal_link_checker(seed_url, full_url):  # Check if it's internal
                website_crawler_and_indexer(full_url, visited_links)  # Recursively calls websit_crawler to crawll all hyperlinks

    #handles all sorts of exceptions (connection error, timeout etc)
    except requests.exceptions.RequestException as e:
        print(f"Error crawling {seed_url}: {e}")


website_crawler_and_indexer(seed_url)



