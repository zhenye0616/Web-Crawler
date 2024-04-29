import re
from urllib.parse import urlparse, urldefrag, urlunparse, urljoin
from bs4 import BeautifulSoup
from urllib.error import HTTPError

def scraper(url, resp):
    # print(url)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(base, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = []
    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        # print()
        text = " ".join(soup.stripped_strings)
        word_count = len(text.split())
        print(word_count)
        print()

        if word_count < 100:
            print("Word count < 100")
            print()
            return links
        if "ics.uci.edu/community/news/view_news" in base:
            print()
            print(text)


        for a in soup.find_all('a',href=True):
            href = a.get('href')
            absolute = urljoin(base,href)
            links.append(urldefrag(absolute)[0])

    elif resp.status == 301 or resp.status == 302:
        # Handle redirects
        location = resp.headers.get('location')
        if location:
            links.append(location)

    elif resp.status == 404:
        # Handle dead URLs
        print(f"Dead URL: {resp.url}")

    else:
        print(f"Error: Status Code {resp.status}")
        print(f"URL: {resp.url}")
        print(resp.error)
        # print(resp.raw_response.content)
        print()
    return links

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    trapLst = ["ics.uci.edu/doku.php","alumni/stayconnected"]
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        for trap in trapLst:
            if trap in url:
                return False
        if parsed.query in {"action=download","action=login","action=edit"}:
            return False
        if not re.match(r".*\.(ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu)",parsed.netloc.lower()):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|img"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|zip"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv|war"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        # print(url)
        # print()
        return True
    except HTTPError as e:
        if e.code == 200:
            print('200 status but empty content or dead URL')
            # A 200 status code but empty content or an error indicates a dead URL
            return False
    except TypeError:
        print ("TypeError for ", parsed)
        raise
