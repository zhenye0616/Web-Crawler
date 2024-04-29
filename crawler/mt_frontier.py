import os
import shelve
from threading import Lock
from queue import Queue, Empty
from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()
        self.save_lock = Lock()  # Lock for protecting self.save

        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exist, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)

        # Load existing save file, or create one if it does not exist.
        with self.save_lock:
            self.save = shelve.open(self.config.save_file)
            if restart:
                for url in self.config.seed_urls:
                    self.add_url(url)
            else:
                # Set the frontier state with contents of the save file.
                self._parse_save_file()
                if not self.save:
                    for url in self.config.seed_urls:
                        self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        with self.save_lock:
            total_count = len(self.save)
            tbd_count = 0
            for url, completed in self.save.values():
                if not completed and is_valid(url):
                    self.to_be_downloaded.append(url)
                    tbd_count += 1
            self.logger.info(
                f"Found {tbd_count} URLs to be downloaded from {total_count} "
                f"total URLs discovered.")

    def get_tbd_url(self):
        with self.save_lock:
            try:
                return self.to_be_downloaded.pop()
            except IndexError:
                return None

    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        with self.save_lock:
            if urlhash not in self.save:
                self.save[urlhash] = (url, False)
                self.save.sync()
                self.to_be_downloaded.append(url)

    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        with self.save_lock:
            if urlhash not in self.save:
                self.logger.error(f"Completed URL {url}, but have not seen it before.")
            else:
                self.save[urlhash] = (url, True)
                self.save.sync()