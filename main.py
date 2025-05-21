from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

def save_links_to_file(links, filename='movie_links.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(f"{link}\n")
    print(f"Links saved to {filename}")
    
user_input = input("Do you want to load the links from a file? (y/n): ").strip().lower()
    
def get_links():
    driver = webdriver.Chrome()

    driver.get("https://www.commonsensemedia.org/movie-reviews#browse-reviews-list")

    wait = WebDriverWait(driver, 20)

    all_links = []

    page = 1




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
        time.sleep(5)
        page += 1

    print(f"\nTotal number of links collected: {len(all_links)}")
    # Save links to text file
    save_links_to_file(all_links)
    driver.quit()

def get_data():
    with open('movie_links.txt', 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f.readlines()]
    driver2 = webdriver.Chrome()
    wait = WebDriverWait(driver2, 20)
    # Process the links as needed
    for link in links:        
        driver2.get(link)         
        driver2.execute_cdp_cmd('Storage.clearDataForOrigin', {
        "origin": '*',
        "storageTypes": 'all',
        })
        wait = WebDriverWait(driver2, 20)
        stars = len(driver2.find_elements(By.CSS_SELECTOR, 'div.review-rating > span > span > i.icon-star-solid.active'))
        movie_name = wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div[1]/div[1]/div[1]/h1')
        )).text
        genre = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'span.detail--genre > a')
        )).text
        date = wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div[1]/div[3]/div/div/div[1]/div/div[7]/div/div/ul/li[1]/span')
        )).text
        rating = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'span.detail--mpaa-rating')
        )).text
        date = date[-4:]
        print(genre, rating)
        time.sleep(2)
        movie_data= [[movie_name, stars, genre, date, rating]]
        
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(movie_data)
    
    print(movie_data)
        

if user_input == 'n':
    get_links()
elif user_input == 'y':
    get_data()
    