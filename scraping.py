import requests
from bs4 import BeautifulSoup
import random
import time
import pandas as pd

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",
]

def scrape_jobs(geoId="", title="", location="", sortBy="DD", pages_to_scrape=10, jobs_per_page=25):
    job_list = []

    for page in range(pages_to_scrape):
        start = page * jobs_per_page
        print(f"\n📄 Scraping page {page+1} ...")

        # ✅ URL modifiée : inclut title, location vides + tri par date descendante (DD)
        list_url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={title}&location={location}&geoId={geoId}&sortBy={sortBy}&start={start}"
        )

        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(list_url, headers=headers)
        time.sleep(random.uniform(6, 8))

        if response.status_code == 429:
            print(f"❌ Trop de requêtes (HTTP 429), pause 10s ...")
            time.sleep(10)
            continue
        elif response.status_code != 200:
            print(f"❌ Erreur HTTP {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        page_jobs = soup.find_all("li")
        if not page_jobs:
            print("⚠️ Plus d’offres disponibles.")
            break

        id_list = []
        for job in page_jobs:
            base_card_div = job.find("div", {"class": "base-card"})
            if base_card_div and base_card_div.get("data-entity-urn"):
                job_id = base_card_div.get("data-entity-urn").split(":")[3]
                id_list.append(job_id)

        print(f"✅ {len(id_list)} offres trouvées sur la page {page+1}")

        for job_id in id_list:
            job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            job_response = requests.get(job_url, headers=headers)
            time.sleep(random.uniform(7, 10))
            if job_response.status_code != 200:
                continue

            job_soup = BeautifulSoup(job_response.text, "html.parser")
            job_post = {}

            title_tag = job_soup.find("h2", {"class": lambda x: x and "top-card-layout__title" in x})
            job_post["job_title"] = title_tag.text.strip() if title_tag else None

            company_tag = job_soup.find("a", {"class": lambda x: x and "topcard__org-name-link" in x})
            job_post["company_name"] = company_tag.text.strip() if company_tag else None

            time_tag = job_soup.find("span", {"class": lambda x: x and "posted-time-ago__text" in x})
            job_post["time_posted"] = time_tag.text.strip() if time_tag else None

            applicants_tag = job_soup.find("span", {"class": lambda x: x and "num-applicants__caption" in x})
            job_post["num_applicants"] = applicants_tag.text.strip() if applicants_tag else None

            job_list.append(job_post)

    df = pd.DataFrame(job_list)
    print(f"\n📊 Nombre total d'offres collectées : {len(df)}")
    return df
