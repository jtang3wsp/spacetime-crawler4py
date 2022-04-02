import pickle


with open('crawlstats.pk', 'rb') as f:
    unique_url, subdomain_dict, word_freq_dict, most_words_page, prev_page_token_freq, total_urls = pickle.load(f)


if total_urls != 0:
    print('Urls left:', total_urls)
print('UNIQUE URLS FOUND:', unique_url)
print('=======================================')
print('SUBDOMAINS FOUND:')
subdomain_dict_sorted = dict(sorted(subdomain_dict.items()))
for k, v in subdomain_dict_sorted.items():
    print(k + ": " + str(v))

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