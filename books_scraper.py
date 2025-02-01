# books_scraper.py

import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import matplotlib.pyplot as plt

def fetch_page(url):
    """Fetch the HTML content of the page."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_books(html_content):
    """Parse the HTML content using BeautifulSoup and extract book details."""
    soup = BeautifulSoup(html_content, 'html.parser')
    books = []

    # Each book is in an article tag with class 'product_pod'
    for book in soup.find_all('article', class_='product_pod'):
        # Get book title (in the 'alt' attribute of the image)
        title = book.find('img')['alt']
        # Get price (in a p tag with class 'price_color')
        price = book.find('p', class_='price_color').get_text(strip=True)

        # Fix encoding issue by removing unwanted characters
        price = price.replace('Â', '').replace('£', '').strip()

        books.append({'Title': title, 'Price': price})
    
    return books


def save_to_csv(data, filename='books.csv'):
    """Save the list of dictionaries to a CSV file."""
    if not data:
        print("No data to save.")
        return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Data saved to {filename}")

def scrape_books():
    """Scrape all pages from the Books to Scrape website."""
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    all_books = []
    page = 1

    while True:
        print(f"Scraping page {page}...")
        url = base_url.format(page)
        html_content = fetch_page(url)
        if not html_content:
            break

        books = parse_books(html_content)
        if not books:  # No books found, likely reached end of pages.
            break

        all_books.extend(books)
        page += 1

    return all_books

def clean_data(csv_filename='books.csv'):
    """Load and clean the data using pandas."""
    df = pd.read_csv(csv_filename, encoding='utf-8')
    
    # Fix potential encoding issues
    df['Price'] = df['Price'].apply(lambda x: x.encode('ascii', 'ignore').decode('ascii'))  

    # Remove the currency symbol (e.g., '£') and convert to float.
    df['Price'] = df['Price'].replace('[^0-9.]', '', regex=True).astype(float)

    return df


def visualize_data(df):
    """Create a simple histogram of book prices."""
    plt.figure(figsize=(10, 6))
    plt.hist(df['Price'], bins=20, color='skyblue', edgecolor='black')
    plt.title('Distribution of Book Prices')
    plt.xlabel('Price (£)')
    plt.ylabel('Number of Books')
    plt.show()

def main():
    # Step 1: Scrape the data
    books = scrape_books()
    if books:
        # Step 2: Save data to CSV
        save_to_csv(books)
    else:
        print("No books were scraped. Exiting.")
        return

    # Step 3: Load and clean the data
    df = clean_data()

    # Display some basic statistics
    print("Data Summary:")
    print(df.describe())

    # Step 4: Visualize the data
    visualize_data(df)

if __name__ == '__main__':
    main()
