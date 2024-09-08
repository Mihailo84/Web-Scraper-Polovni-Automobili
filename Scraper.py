import requests
from bs4 import BeautifulSoup
import re

from lxml.doctestcompare import strip


class CarScraper:
    def __init__(self, url):
        self.url = url

    def scrape(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(self.url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            #Koristi se soup.select da se pronadju sve kartice pod tagom
            #article i sa klasom classified gde se nalaze podaci o autu koji mi trebaju
            car_info_section = soup.select('article.classified')
            if not car_info_section:
                print("No car information found")
                return None

            cars_data = []
            for car in car_info_section:
                #print(car) u car se u ovom momentu nalazi komplet html za article
                car_data = {}
                try:
                    # Uzima prema putanji klase .price
                    price_element = car.select_one('.price')
                    if price_element:  # Remove everything from the price string that isn't a number
                        price_text = price_element.get_text(strip=True)
                        price = re.sub(r'[^\d]', '', price_text)
                        car_data['price'] = int(price) if price else 0  # Convert to integer instead of float
                    else:
                        car_data['price'] = 0

                    # Uzima godinu prema putanji klasa .setInfo i .top
                    year_type_element = car.select_one('.setInfo .top')
                    if year_type_element:
                        year_text = year_type_element.get_text(strip=True)
                        year_match = re.match(r'(\d{4})', year_text)
                        car_data['year'] = int(year_match.group(1)) if year_match else 0
                    else:
                        car_data['year'] = 0  # Handle missing year/type

                    # Uzima podatke za motor i skida sve sem broja kubikaze(ili kako se vec zove)
                    engine_element = car.select_one('.setInfo .bottom')
                    if engine_element:
                        engine_text = engine_element.get_text(strip=True)
                        car_data['engine'] = re.sub(r'[^\d]', '', engine_text)
                    else:
                        car_data['engine'] = 'MISSING'

                    location_element = car.select_one('.city')
                    if location_element:
                        car_data['location'] = location_element.get_text(strip=True)
                    else:
                        car_data['location'] = 'MISSING'

                    top_elements = car.select('.setInfo .top') #ima ista putanja do godine pa onda mora ovako
                    if len(top_elements) > 1:
                        mileage_text = top_elements[1].get_text(strip=True)
                        mileage_cleaned = re.sub(r'[^\d]', '', mileage_text)  # Clean the mileage text
                        car_data['mileage'] = int(mileage_cleaned) if mileage_cleaned else 0
                    else:
                        car_data['mileage'] = 'MISSING'



                except AttributeError as e:
                    print(f"Error parsing car data: {e}")
                    continue
                cars_data.append(car_data)

            return cars_data
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
