from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse

class LinkChecker:
    def __init__(self, url):
        self.url = url
        self.visited_links = set()
        self.driver = None
        self.good_links = []
        self.bad_links = []

    def check_links(self):
        # Set up ChromeDriver with headless option
        if self.driver is None:
            options = Options()
            # options.headless = True
            options.add_argument('--headless')
            self.driver = webdriver.Chrome(options=options)

        # Navigate to the website
        self.driver.get(self.url)

        # Wait for JavaScript to render
        self.driver.implicitly_wait(10)

        # Get all URLs to follow up
        links = self.driver.find_elements(By.TAG_NAME, "a")    
        for link in links:
            href = link.get_attribute('href')
            if href is not None:
                parsed_url = urlparse(href)
                if parsed_url.netloc == '':
                    full_url = self.driver.current_url + href
                else:
                    full_url = href
                if not (full_url.endswith('.jpg') or full_url.endswith('.jpeg') or full_url.endswith('.png') or full_url.endswith('.gif') or full_url.endswith('.js') or full_url.endswith('.css')):
                    if full_url not in self.visited_links:
                        self.visited_links.add(full_url)
                        self.driver.get(full_url)
                        if self.driver.title == '404 Not Found':
                            self.bad_links.append(full_url)
                        else:
                            self.good_links.append(full_url)
                        self.check_links()

        if self.driver.current_url == self.url:
            # Quit the browser
            self.driver.quit()

        return self.good_links, self.bad_links, self.visited_links

if __name__ == '__main__':
    link_checker = LinkChecker('https://redesign.marketvector.com')
    good_links, bad_links, visited_links = link_checker.check_links()
    print('Good links:')
    for good_link in good_links:
        print(good_link)
    print('Bad links:')
    for bad_link in bad_links:
        print(bad_link)
