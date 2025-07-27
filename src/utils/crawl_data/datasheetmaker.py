from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime

# Configuration
CHROMEDRIVER_PATH = r"C:\Code\chromedriver-win64\chromedriver.exe"
BASE_URL = "https://nhathuoclongchau.com.vn/thuoc/thuoc-mat-tai-mui-hong"

# Create output filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"ear_nose_throat_medicines_{timestamp}.xlsx"

# Browser configuration
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

# Access the main page
driver.get(BASE_URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h3")))
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)

# Get list of medicine links
soup = BeautifulSoup(driver.page_source, 'html.parser')
product_tags = soup.select('a[href^="/thuoc/"]')
product_links = list(set(["https://nhathuoclongchau.com.vn" + a['href'] for a in product_tags]))
print(f"🔗 Found {len(product_links)} medicine links.")

# Function to parse structured side effects
def parse_side_effects_structured(soup):
    symptoms = []
    all_ps = soup.find_all('p')
    for idx, p in enumerate(all_ps):
        if p.find('i') and re.search(r"(Common|Uncommon|Rare|Unknown frequency)", p.get_text(), re.IGNORECASE):
            for next_tag in all_ps[idx+1:]:
                if next_tag.name == 'ul':
                    for li in next_tag.find_all('li'):
                        text = li.get_text(" ", strip=True)
                        match = re.match(r"[^:]+:\s*(.+)", text)
                        raw = match.group(1) if match else text
                        clean = re.sub(r"\([^)]*\)", "", raw)
                        for sym in clean.split(","):
                            s = sym.strip().capitalize()
                            if s and s not in symptoms:
                                symptoms.append(s)
                    break
    return ", ".join(symptoms)

# Fallback function to extract side effects block from <h2>/<h3>
def extract_side_effects_block(soup):
    for tag in soup.find_all(["h2", "h3"]):
        if "side effects" in tag.get_text(strip=True).lower():
            texts = []
            for sibling in tag.find_next_siblings():
                if sibling.name in ["h2", "h3"]:
                    break
                texts.append(sibling.get_text(" ", strip=True))
            return "\n".join(texts).strip()
    return ""

# Start crawling each medicine
medicines = []
crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for link in product_links:
    print(f"🔍 Crawling: {link}")
    try:
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        med_soup = BeautifulSoup(driver.page_source, 'html.parser')

        name_tag = med_soup.select_one('h1[data-test="product_name"]') or med_soup.select_one("h1.product-title")
        name = name_tag.text.strip() if name_tag else f"Unknown name - {link}"

        # Main indication
        main_indication = "Unknown"
        for h3 in med_soup.find_all("h3"):
            if "indication" in h3.get_text(strip=True).lower():
                indication_parts = []
                for tag in h3.find_next_siblings():
                    if tag.name == "h3" and "pharmacodynamics" in tag.get_text(strip=True).lower():
                        break
                    if tag.name in ["p", "ul", "ol"]:
                        text = tag.get_text(" ", strip=True)
                        if text:
                            indication_parts.append(text)
                if indication_parts:
                    main_indication = "\n".join(indication_parts)
                break

        # Side effects
        side_effects = parse_side_effects_structured(med_soup)
        if not side_effects:
            side_effects = extract_side_effects_block(med_soup)
        if not side_effects:
            side_effects = "Not found"

        medicines.append({
            "Medicine Name": name,
            "Main Indications": main_indication,
            "Side Effects": side_effects,
            "Crawl Timestamp": crawl_time
        })

    except Exception as e:
        print(f"❌ Error at {link}: {e}")

driver.quit()

# Save as a new Excel file
df = pd.DataFrame(medicines)
df.to_excel(output_filename, index=False)
print(f"✅ Data saved to {output_filename}")
