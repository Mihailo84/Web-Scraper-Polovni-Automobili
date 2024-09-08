import discord
import re
from datetime import datetime
from Scraper import CarScraper

class DiscordBot:
    def __init__(self, token):
        self.token = token

        intents = discord.Intents.default()
        intents.message_content = True

        self.client = discord.Client(intents=intents)

        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    async def on_ready(self):
        print(f"Logged in as {self.client.user}")

    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if message.content == "!CAR":
            await message.channel.send("Sacekaj, prikupljamo podatke...")

            scraper = CarScraper("https://www.polovniautomobili.com/auto-oglasi/pretraga?brand=opel&model%5B%5D=astra&brand2=&price_from=&price_to=&year_from=&year_to=&chassis%5B%5D=278&flywheel=&atest=&door_num=&submit_1=&without_price=1&date_limit=&showOldNew=all&modeltxt=&engine_volume_from=&engine_volume_to=&power_from=&power_to=&mileage_from=&mileage_to=&emission_class=&seat_num=&wheel_side=&registration=&country=&country_origin=&city=&registration_price=&page=&sort=")
            car_data = scraper.scrape() #ovde je lista svih auta sa svojim podacima

            if car_data:
                for car in car_data:
                    car['score'] = self.calculate_points(car)
                    print(car)

                best_car = car_data[0]
                for car in car_data:
                    if car['score'] > best_car['score']:
                        best_car = car

                # Poruka koja se salje na diskord
                best_car_message = f"Best car:\n\t{best_car} \nScore:\n\t{best_car['score']}"
                await message.channel.send(best_car_message)
            else:
                await message.channel.send("No car data found.")

    def calculate_points(self, car):
        price = int(car.get('price', 0))
        year = int(car.get('year', 0))
        mileage = float(car.get('mileage', 0))

        points = self.calculate_points_based_on_price_year_mileage(price, year, mileage)
        return round(points, 2)

    def calculate_points_based_on_price_year_mileage(self, price, year, mileage):
        max_points = 100

        current_year = 2024
        age = current_year - year

        price_points = max_points - (price / 1000)
        year_points = max_points - (age * 2)
        mileage_points = max_points - (mileage / 10000)

        return price_points + year_points + mileage_points

    def run(self):
        self.client.run(self.token)
