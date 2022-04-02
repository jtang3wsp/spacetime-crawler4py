import pickle


unique_url = 0  # number of unique urls found
subdomain_dict = dict()  # dictionary of subdomains and their frequencies
word_freq_dict = dict()  # dictionary of words and their frequencies
most_words_page = ["", 0]  # tuple containing the url of the page with the most words, and that number of words
prev_page_token_freq = dict()  # dictionary to store the previous page's token frequency
total_urls = 0  # number of total urls to download


def print_subdomains():
        print('UNIQUE URLS FOUND:', unique_url)
        print('=======================================')
        print('SUBDOMAINS FOUND:')
        subdomain_dict_sorted = dict(sorted(subdomain_dict.items()))
        for k, v in subdomain_dict_sorted.items():
            print(k + ": " + str(v))

def print_top_fifty_words():
        print('=======================================')
        print(f'Longest page was {most_words_page[0]} with {most_words_page[1]} words')
        print('=======================================')
        print('Top 50 most common words:')
        word_freq_dict_sorted = dict(sorted(word_freq_dict.items(), key=lambda item: -item[1]))
        count = 1
        for k, v in word_freq_dict_sorted.items():
            print(f'{count}. {k}: {v}')
            count+=1
            if(count >= 51):
                break


def load_stats(filename):
    global unique_url, subdomain_dict, word_freq_dict, most_words_page, prev_page_token_freq, total_urls
    with open(filename, 'rb') as f:
        unique_url, subdomain_dict, word_freq_dict, most_words_page, prev_page_token_freq, total_urls = pickle.load(f)


def save_stats(filename):
    with open(filename, 'wb') as f:
        pickle.dump([unique_url, subdomain_dict, word_freq_dict, most_words_page, prev_page_token_freq, total_urls], f)