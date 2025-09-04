import requests
from bs4 import BeautifulSoup
import os
import boto3
import time

BUCKET_NAME = "poke-scraper-ouiza"

s3 = boto3.client("s3")

URL = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

os.makedirs("images", exist_ok=True)

for img in soup.select("table a img"):
    name = img["alt"]
    img_url = img["src"]

    if img_url.startswith("//"):
        img_url = "https:" + img_url

    filename = os.path.join("images", f"{name}.png")

    try:
        
        resp = requests.get(img_url, timeout=10)
        resp.raise_for_status()  # Erreur si pas de 200
        with open(filename, "wb") as f:
            f.write(resp.content)
        print(f"Téléchargé : {filename}")

        s3_key = f"images/pokemons/{name}.png"
        s3.upload_file(filename, BUCKET_NAME, s3_key)
        print(f"Uploadé dans S3 : {s3_key}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau pour {name} : {e}")
        continue
    except Exception as e:
        print(f"Erreur générale pour {name} : {e}")
        continue

    time.sleep(1)

