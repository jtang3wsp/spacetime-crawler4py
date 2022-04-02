import re
import counters
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from urllib import parse
from bs4 import BeautifulSoup
import math


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # inspiration: https://stackoverflow.com/questions/5815747/beautifulsoup-getting-href
    
    url_set = set()

    # Checks if the page content is past a certain threshold
    if resp.raw_response is not None:
        print(f"========================================\nLENGTH OF HTML: {len(resp.raw_response.content)}")
        if len(resp.raw_response.content) > 2000000 or len(resp.raw_response.content) < 900: # avoid very large and very small sites
            return list(url_set)
        
    if is_valid(resp.url) and is_in_domain(resp.url) and resp.error == None and resp.status == 200:
        page_content = BeautifulSoup(resp.raw_response.content, "html.parser")
        tokenized = tokenize_page(page_content, resp.url)
        if tokenized[1] >= 100:
            unique_url_and_subdomain_tracker(url)
            if tokenized[0] > 0.31: # if similarity <= 0..31 or less than 100 tokens, do not scrape for urls
                # Add a '/' to the url before joining it with the hrefs
                unnormalized_url = resp.url
                if ends_with_file(resp.url) == False:
                    unnormalized_url = resp.url + '/'

                for a_tag in page_content.find_all('a', href=True):
                    temp_path = a_tag['href']
                    if temp_path.startswith('javascript'):  # is javascript; skip over a_tag
                        continue
                    temp_path = parse.urldefrag(temp_path)[0]
                    temp_path = parse.urljoin(unnormalized_url, temp_path)
                    if is_low_info(temp_path) is None and is_in_domain(temp_path) and is_valid(temp_path) and is_repeating(temp_path) is None:
                        url_set.add(temp_path)
    print('found url:', len(url_set))
    return list(url_set)


def unique_url_and_subdomain_tracker(url) -> None:
    """Counts all the valid unique urls and tracks subdomains under ics.uci.edu"""
    counters.unique_url += 1
    print(f'Unique URL count: {counters.unique_url}\n========================================')

    parsed = parse.urlparse(url).netloc.lower()
    if re.search(r".*\.ics\.uci\.edu.*", parsed) != None and parsed.startswith('www') == False:
        subdomain_name = parsed
        
        if subdomain_name not in counters.subdomain_dict:
            counters.subdomain_dict[subdomain_name] = 1
            print('*****Subdomain found:', subdomain_name)
        else:
            counters.subdomain_dict[subdomain_name] += 1
            if (counters.subdomain_dict[subdomain_name] != 0 and counters.subdomain_dict[subdomain_name] % 25 == 0):
                print('*****Subdomain count:', subdomain_name, counters.subdomain_dict[subdomain_name])


# Tokenizes a given page, filtering out stopwords and punctuation
def tokenize_page(page_content, url: str):
    stop_words_set = set(stopwords.words('english'))
    word_tokens_list = word_tokenize(page_content.get_text())
    filtered_page = [word.lower() for word in word_tokens_list if len(word) > 1 and not word.lower() in stop_words_set and word.isalnum() == True]
    page_token_freq = compute_word_freq(filtered_page)
    similarity = compute_similarity(page_token_freq, counters.prev_page_token_freq)
    print(f"Similarity between current and previous page: {similarity}")
    print(f"Number of tokens: {len(filtered_page)}")
    print(f"Number of unique tokens: {len(page_token_freq)}")

    if similarity <= 0.31 or len(filtered_page) < 100: # if the pages are too similar or the page has low textual info, don't add its words to total stats
        return [similarity, len(filtered_page)]
    else:
        if counters.most_words_page[1] < len(filtered_page):
            counters.most_words_page[0] = url
            counters.most_words_page[1] = len(filtered_page)
        for token in page_token_freq:
            if token not in counters.word_freq_dict.keys():
                counters.word_freq_dict[token] = page_token_freq[token]
            else:
                counters.word_freq_dict[token] += page_token_freq[token]
        counters.prev_page_token_freq = page_token_freq
        return [similarity, len(filtered_page)]


# Returns a dictionary of token frequency in a page
def compute_word_freq(token_list):
    token_freq = dict()
    for token in token_list:
        if token not in token_freq:
            token_freq[token] = 1
        else:
            token_freq[token] += 1
    return token_freq


# Computes textual similarity between two pages/dictionaries; 0 = exact same page
# https://www.geeksforgeeks.org/measuring-the-document-similarity-in-python/
def compute_similarity(D1, D2):
    numerator = dotProduct(D1, D2)
    denominator = math.sqrt(dotProduct(D1, D1)*dotProduct(D2, D2))
    if denominator == 0: # prevents divide by zero errors
        denominator = 0.01
    return math.acos(numerator / denominator)


def dotProduct(D1, D2):
    s = 0.0
    for key in D1:
        if key in D2:
            s += (D1[key] * D2[key])
    return s


def ends_with_file(url):
    return url.endswith('.txt') or url.endswith('.php') or url.endswith('.html') or url.endswith('.htm') or url.endswith('.shtml') or url.endswith('.xhtml')


def is_in_domain(url):
    return re.search(r"(.*\.ics\.uci\.edu|.*\.cs\.uci\.edu"
            + r"|.*\.informatics\.uci\.edu|.*\.stat\.uci\.edu|today\.uci\.edu)$", parse.urlparse(url).netloc.lower())


def is_low_info(url):
    return re.search(r"(.*mailto:.*|.*tel:.*|.*blog.*|.*calendar.*|.*action=.*|.*replytocom=.*|.*share=.*|.*ical=.*|.*wp-content\/uploads.*|.*pdf.*|.*\.png.*"
                    + r"|.*date=.*|.*sort=.*|.*view=.*|.*[\?&]filter.*|.*=sidebyside.*|.*=media.*|.*idx=.*|.*rev=.*|.*do=(login|edit|revisions|recent).*"
                    + r"|.*from=.*|.*\/sld[0-9]+?\.htm)", url.lower())


def is_repeating(url):
    return re.search(r"(?:(\/\w+)(?:.+?\1){2,}|(\/\w+)?\2)", parse.urlparse(url).path)


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = parse.urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv|odc"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|war|apk|img|wmz|sql|bam)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
