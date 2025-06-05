import concurrent
import time
import csv
import math
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

# Turning off images and putting it in headless mode
options = Options()
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument('--headless=new')
service = Service('./chromedriver-win64/chromedriver.exe')
all_links = []
# This grabs all the data from a single movie review page
def process_chunk(links_chunk):
    driver2 = webdriver.Chrome(service=service, options=options)
    driver2.set_window_size(3840, 2160)
    wait = WebDriverWait(driver2, 30)
    chunk_data = []
    try:
        for link in links_chunk:
            try:
                driver2.get(link)
                driver2.execute_cdp_cmd('Storage.clearDataForOrigin', {
                    "origin": '*',
                    "storageTypes": 'all',
                })
                custom_wait_clickable_and_click(wait.until(EC.element_to_be_clickable(
                    (By.XPATH,
                     '/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div[1]/div[3]/div/div/div[1]/div/div[7]/div/button'))))
                time.sleep(3)

                stars = len(driver2.find_elements(By.CSS_SELECTOR,
                                                  'div.review-rating > span > span > i.icon-star-solid.active'))
                movie_name = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div[1]/div[1]/div[1]/h1')
                )).text
                genre_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'span.detail--genre > a')
                ), "Unknown")
                genre = genre_element.text if (genre_element.text != '') else "Unknown"
                if genre == "Unknown":
                    print(f"Skipping movie with unknown genre: {movie_name}")
                    continue
                date = wait.until(EC.presence_of_element_located(
                    (By.XPATH,
                     '/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div[1]/div[3]/div/div/div[1]/div/div[7]/div/div/ul/li[1]/span')
                )).text
                rating = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'span.detail--mpaa-rating')
                )).text
                date = date[-4:]
                print(f"Processed: {movie_name} - {genre} {rating}")
                chunk_data.append([movie_name, stars, genre, date, rating])

            except Exception as e:
                print(f"Error processing link {link}: {str(e)}")
                continue

    finally:
        driver2.quit()

    return chunk_data

# Saves the links to a txt file
def save_links_to_file(links, filename='movie_links.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(f"{link}\n")
    print(f"Links saved to {filename}")

# Grabs all the links from the movie review site
def process_page_chunk(page_numbers):
    links = []
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.commonsensemedia.org/movie-reviews#browse-reviews-list")
    wait = WebDriverWait(driver, 20)

    try:
        current_page = 1
        for target_page in page_numbers:
            try:
                # Navigate through pages until we reach our target page
                while current_page < target_page:
                    next_button = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, 'li.pagination__next > button')
                    ))
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(5)
                    current_page += 1

                # Get links from current page
                linksName = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, '//*[@id="browse-reviews-list"]/div/div/div//div[2]/h3/a[@href]')
                ))

                current_page_links = []
                for e in linksName:
                    link = e.get_attribute('href')
                    current_page_links.append(link)

                links.extend(current_page_links)
                print(f"Thread processed page {target_page}: Found {len(current_page_links)} links")

            except Exception as e:
                print(f"Error processing page {target_page}: {str(e)}")
                continue

    finally:
        driver.quit()

    return links

# Saves the links and does them in parallel
def get_links(num_pages=10, num_threads=1):
    page_numbers = list(range(1, num_pages + 1))

    # number of threads asked as going one by one takes too long

    # splits up workload evenly
    chunk_size = math.ceil(len(page_numbers) / num_threads)
    page_chunks = [page_numbers[i:i + chunk_size] for i in range(0, len(page_numbers), chunk_size)]



    print(f"Starting link collection with {num_threads} threads...")

    # Process chunks in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_results = [executor.submit(process_page_chunk, chunk) for chunk in page_chunks]

        for future in concurrent.futures.as_completed(future_results):
            chunk_links = future.result()
            all_links.extend(chunk_links)

    # prints out the total number of links collected
    print(f"Total links found: {len(all_links)}")

    # saves links to file which is used for importing
    with open('movie_links.txt', 'w', encoding='utf-8') as f:
        for link in all_links:
            f.write(f"{link}\n")

    print(f"Links saved to movie_links.txt")
    print("\nLink collection completed. Starting data processing...")
    get_data(all_links)

# custom click as default wasn't working for me
def custom_wait_clickable_and_click(selector):
  count = 0
  while count < 5:
    try:
      time.sleep(7)
      elem = selector
      elem.click()
      return elem

    except WebDriverException as e:
      if 'is not clickable at point' in str(e):
        print('Retrying clicking on button.')
        count = count + 1
      else:
        raise e

  raise TimeoutException('custom_wait_clickable timed out')

# Processes the links for parallel processing and refines the data
def get_data(links=None, num_threads=1):
    if links is None:
        # If no links provided, read from file
        with open('movie_links.txt', 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f.readlines()]

    # slipts up the workload evenly for the threads
    chunk_size = math.ceil(len(links) / num_threads)
    link_chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]

    all_movie_data = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_results = [executor.submit(process_chunk, chunk) for chunk in link_chunks]

        for future in future_results:
            chunk_results = future.result()
            all_movie_data.extend(chunk_results)

    genre_stars = defaultdict(list)

    # grabs all the genres and their ratings
    for row in all_movie_data:
        genre = row[2]
        stars = row[1]
        genre_stars[genre].append(stars)

    # uses stars to calculate average ratings for each genre
    genre_averages = {genre: (round(sum(stars) / len(stars), 2), len(stars))
              for genre, stars in genre_stars.items()}

    sorted_genres = sorted(genre_averages.keys())
    minimal_data = [[genre_averages[genre] for genre in sorted_genres]]
    headers_full = ['Movie Name', 'Stars', 'Genre', 'Release Year', 'MPAA Rating']

    print(genre_averages)
    # saves data to csv file for gui and other uses
    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers_full)
        writer.writerows(all_movie_data)

    with open('output_genre_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Genre', 'Average Stars', 'Count'])
        for genre, (average, count) in genre_averages.items():
            writer.writerow([genre, average, count])

    print(f"Total movies processed: {len(all_movie_data)}")
    print("\nAverage stars by genre:")
    genre_ratings = []
    for genre in sorted_genres:
        avg_stars, count = genre_averages[genre]
        genre_ratings.append([genre, avg_stars])
        print(f"{genre}: {avg_stars}")
    print(f"Total movies processed: {len(all_movie_data)}")
    print("\nAverage stars by genre:")
    # Gather movies by name length and calculate average stars
    name_length_to_stars = {}
    for movie in all_movie_data:
        movie_name = movie[0]  # Movie name
        stars = movie[1]       # Movie stars
        name_length = len(movie_name)
        if name_length not in name_length_to_stars:
            name_length_to_stars[name_length] = []
        name_length_to_stars[name_length].append(stars)

    name_length_to_average_stars = {
    name_length: round(sum(stars) / len(stars), 2)
    for name_length, stars in name_length_to_stars.items()
}

# sort the lengths by numbers increasing
    sorted_name_lengths = sorted(name_length_to_average_stars.items())

    print("\nAverage Stars by Movie Name Length:")
    for name_length, avg_stars in sorted_name_lengths:
        print(f"Name Length: {name_length}, Average Stars: {avg_stars}")

    csv_filename = "name_length_to_average_stars.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Name Length", "Average Stars"])
        for name_length, avg_stars in sorted_name_lengths:
            writer.writerow([name_length, avg_stars])
    genre_by_year = defaultdict(lambda: defaultdict(int))
    total_movies_per_year = defaultdict(int)
    for movie in all_movie_data:
        year = movie[3]  # Release Year
        genre = movie[2]  # Genre
        genre_by_year[year][genre] += 1
        total_movies_per_year[year] += 1

    # Calculate percentages for all genres per year
    genre_distribution_data = []
    for year in sorted(genre_by_year.keys()):
        year_data = genre_by_year[year]
        total_movies = total_movies_per_year[year]
        for genre, count in year_data.items():
            percentage = round((count / total_movies) * 100, 2)
            genre_distribution_data.append([year, genre, percentage])

    # Save genre distribution data to CSV
    with open('genre_distribution.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Year', 'Genre', 'Percentage'])
        writer.writerows(genre_distribution_data)

    print("\nGenre Distribution Over Time:")
    for year, genre, percentage in genre_distribution_data:
        print(f"Year {year}: {genre} ({percentage}%)")

    return all_movie_data, genre_averages, name_length_to_average_stars, genre_distribution_data
