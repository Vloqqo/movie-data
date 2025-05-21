from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

driver.get("https://www.commonsensemedia.org/movie-reviews#browse-reviews-list")

wait = WebDriverWait(driver, 20)

all_links = []

page = 1

def save_links_to_file(links, filename='movie_links.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(f"{link}\n")
    print(f"Links saved to {filename}")


while page <= 2572:
    # Grabs and waits for a links to load
    linksName = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, '//*[@id="browse-reviews-list"]/div/div/div//div[2]/h3/a[@href]')
    ))

    current_page_links = []
    for e in linksName:
        link = e.get_attribute('href')
        current_page_links.append(link)

    all_links.extend(current_page_links)
    print(f"Page {page}: Added {len(current_page_links)} links. Total: {len(all_links)}")

    # Save progress every 10 pages
    if page % 10 == 0:
        save_links_to_file(all_links)

    next_button = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'li.pagination__next > button')
    ))
    # Scrolls to bottom for button to appear
    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
    time.sleep(1)
    # Click to next page
    driver.execute_script("arguments[0].click();", next_button)

    # Wait for page to load
    time.sleep(3)
    page += 1

print(f"\nTotal number of links collected: {len(all_links)}")
# Save links to text file
save_links_to_file(all_links)
driver.quit()




