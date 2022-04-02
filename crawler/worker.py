from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import counters
import os.path


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        if os.path.exists('crawlstats.pk'):
            counters.load_stats('crawlstats.pk')
            print("Stats loaded successfully")
        else:
            print("Stats file does not exist")
            
        while (True):
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            print(f'*****{counters.total_urls} URLS LEFT*****')
            resp = download(tbd_url, self.config, self.logger)

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            counters.save_stats('crawlstats.pk')
            time.sleep(self.config.time_delay)

        counters.print_subdomains()
        counters.print_top_fifty_words()
