import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import deathbycaptcha

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # Replace with your driver, e.g., webdriver.Firefox()
driver.get("https://www.sci.gov.in/daily-order-case-no/")

# Initialize DeathByCaptcha client (optional, for CAPTCHA)
captcha_client = deathbycaptcha.SocketClient('username', 'password')

# Data storage
cases = []

# Define function to solve CAPTCHA (mock example)
def solve_captcha():
    # Add actual CAPTCHA-solving logic here
    captcha_path = "captcha_image.png"  # Placeholder for CAPTCHA image path
    captcha = captcha_client.decode(captcha_path)
    if captcha:
        return captcha["text"]
    else:
        print("CAPTCHA solution failed.")
        return None

# Function to scrape page content
def scrape_page():
    try:
        # Use BeautifulSoup to parse page content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Locate case elements
        case_elements = soup.find_all('div', class_='case-info')  # Example class name
        
        for case in case_elements:
            title = case.find('h4').text.strip()
            date = case.find('span', class_='date').text.strip()
            summary = case.find('p', class_='summary').text.strip()
            
            cases.append({
                "Title": title,
                "Date": date,
                "Summary": summary
            })
    except Exception as e:
        print(f"Error scraping page: {e}")

# Navigate through pagination
for i in range(1, 6):  # Limit to first 5 pages as an example
    print(f"Scraping page {i}")
    
    # Attempt to solve CAPTCHA if present
    if "captcha" in driver.page_source:
        captcha_text = solve_captcha()
        if captcha_text:
            # Enter CAPTCHA text in input field (adjust locator as needed)
            captcha_input = driver.find_element(By.ID, 'captchaInput')
            captcha_input.send_keys(captcha_text)
            driver.find_element(By.ID, 'submitCaptcha').click()
            WebDriverWait(driver, 10).until(EC.staleness_of(captcha_input))
    
    # Wait for content to load
    time.sleep(2)
    scrape_page()
    
    # Move to next page if pagination available
    try:
        next_button = driver.find_element(By.LINK_TEXT, 'Next')
        next_button.click()
        WebDriverWait(driver, 10).until(EC.staleness_of(next_button))
    except Exception as e:
        print(f"No more pages to navigate: {e}")
        break

# Save results to CSV
df = pd.DataFrame(cases)
df.to_csv("court_cases.csv", index=False)

print("Scraping completed. Data saved to court_cases.csv.")
driver.quit()
