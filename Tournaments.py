from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time as tm
import json
import re
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, date


class TournamentInfo:
    name: str
    tournament_date: date
    city: str
    areal: str
    capacity: int
    signed: int
    price: int
    start: str
    organizer: str
    category: str
    level: str
    link: str

    def __init__(
        self,
        name,
        tournament_date,
        city,
        areal,
        capacity,
        signed,
        price,
        start,
        organizer,
        category,
        level,
        link,
    ):
        self.name = name
        self.tournament_date = tournament_date
        self.city = city
        self.areal = areal
        self.capacity = capacity
        self.signed = signed
        self.price = price
        self.start = start
        self.organizer = organizer
        self.category = category
        self.level = level
        self.link = link


class Tournaments:
    tournament_list: list()

    def __init__(self) -> None:
        self.tournament_list = []

    def get_category_by_name(self, name):
        if name:
            name_lower = name.lower()
            if "mix" in name_lower:
                return "Mixy"
            elif "muz" in name_lower or "muž" in name_lower:
                return "Muži"
            elif "zen" in name_lower or "žen" in name_lower:
                return "Ženy"
        return "Jiné"

    def open_chrome_with_url(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        driver.maximize_window()
        driver.get(url)
        return driver

    def get_pbt_data(self):
        tournament_areal = "Prague Beach Team (Střešovice)"
        tournament_city = "Praha"
        url = "https://www.praguebeachteam.cz/mobile/#/embedded/anonymous/events/tournaments"
        driver = self.open_chrome_with_url(url)
        main_content = driver.find_element(By.CLASS_NAME, "event-list-container")
        tm.sleep(3)
        print("checkpoint 1")
        days = main_content.find_elements(By.CSS_SELECTOR, "ul.list-group")
        tm.sleep(3)
        print("checkpoint 2")
        for day in days:
            wait = WebDriverWait(driver, 10)
            tournament_overview = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "event-list-container"))
            )
            tm.sleep(3)
            print("checkpoint 3")

            day_and_date = day.find_elements(By.TAG_NAME, "li")
            tournament_date = day_and_date[0].text.split(" ")[1]
            tournament_name = day.find_element(By.CLASS_NAME, "primary-caption").text
            signed, capacity = (day.find_element(By.CLASS_NAME, "capacity").text).split(
                "/"
            )
            organizer = (
                day.find_element(By.CLASS_NAME, "info-caption")
                .text.split(":")[1]
                .strip()
            )
            # deadline = day.find_element(By.CLASS_NAME, "deadline-caption").text
            start_time = (
                day.find_element(By.CLASS_NAME, "start-caption")
                .text.split(":")[1]
                .strip()
            )

            day.click()
            wait = WebDriverWait(driver, 10)
            tournament_detail = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "description"))
            )

            price1, price2 = list(
                map(
                    int,
                    re.findall(
                        r"\d+",
                        tournament_detail.find_elements(By.CLASS_NAME, "value")[3].text,
                    ),
                )
            )
            price = max(price1, price2) * 2

            driver.back()

            category = self.get_category_by_name(tournament_name)

            link = "https://www.praguebeachteam.cz/?menu=open-turnaje"

            if tournament_areal not in self.tournament_list:
                self.tournament_list[tournament_areal] = []

            self.tournament_list[tournament_areal].append(
                TournamentInfo(
                    name=tournament_name,
                    tournament_date=tournament_date,
                    city=tournament_city,
                    areal=tournament_areal,
                    capacity=capacity,
                    signed=signed,
                    price=price,
                    start=start_time,
                    organizer=organizer,
                    category=category,
                    level="Hobby/Open",
                    link=link,
                ).__dict__()
            )
        driver.quit()

    def get_ladvi_data(self):
        tournament_areal = "Beachklub Ládví"
        tournament_city = "Praha"
        url = "https://beachklubladvi.cz/beachvolejbal/beach-turnaje/"
        driver = self.open_chrome_with_url(url)
        tournament_table = driver.find_element(By.ID, "turnaj_flb_event_list")

        number_of_tournaments = len(
            tournament_table.find_elements(By.CLASS_NAME, "flb_event_list_item")
        )
        driver.quit()
        for tournament_id in range(number_of_tournaments):
            driver = self.open_chrome_with_url(url)
            tournament_table = driver.find_element(By.ID, "turnaj_flb_event_list")
            details = tournament_table.find_elements(
                By.CLASS_NAME, "flb_event_list_item_button_detail"
            )[tournament_id].click()
            tm.sleep(3)

            wait = WebDriverWait(driver, 10)
            new_content = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "flb_event_detail"))
            )

            tournament_name = new_content.find_element(
                By.CLASS_NAME, "flb_event_name"
            ).text

            tournament_date_str, start = new_content.find_element(
                By.CLASS_NAME, "flb_event_start"
            ).text.split(" ")

            date_format = "%d.%m.%Y"

            if start[0] == "0":
                start = start[1:]

            tournament_date = datetime.strptime(tournament_date_str, date_format)
            organizer = (
                new_content.find_element(By.CLASS_NAME, "flb_event_organiser")
                .find_element(By.CLASS_NAME, "fullname")
                .text
            )

            price = new_content.find_element(
                By.CLASS_NAME, "flb_event_price"
            ).text.split(",")[0]

            capacity, free = list(
                map(
                    int,
                    re.findall(
                        r"\d+",
                        new_content.find_element(
                            By.CLASS_NAME, "flb_event_places"
                        ).text,
                    ),
                )
            )
            signed = int(capacity) - int(free)

            link = driver.current_url

            category = self.get_category_by_name(tournament_name)

            self.tournament_list.append(
                TournamentInfo(
                    name=tournament_name,
                    tournament_date=tournament_date,
                    city=tournament_city,
                    areal=tournament_areal,
                    capacity=capacity,
                    signed=signed,
                    price=price,
                    start=start,
                    organizer=organizer,
                    category=category,
                    level="Hobby/Open",
                    link=link,
                )
            )
            driver.quit()

    def get_cvf_data(self):
        tournament_areal = "Beachklub Ládví"
        tournament_city = "Praha"
        url_muzi = (
            "https://www.cvf.cz/beach/turnaje/?rok=2023&mesic=&kategorie=Muži&slozka="
        )
        url_zeny = (
            "https://www.cvf.cz/beach/turnaje/?rok=2023&mesic=&kategorie=Ženy&slozka="
        )
        driver = self.open_chrome_with_url(url_muzi)
        tm.sleep(10)
        # tournament_table = driver.find_element(By.ID, "turnaj_flb_event_list")

        # category = self.get_category_by_name(tournament_name)

        # if tournament_areal not in self.tournament_list:
        #     self.tournament_list[tournament_areal] = []

        # self.tournament_list[tournament_areal].append(
        #     TournamentInfo(
        #         name=tournament_name,
        #         date=tournament_date,
        #         city=tournament_city,
        #         areal=tournament_areal,
        #         capacity=capacity,
        #         signed=signed,
        #         price=price,
        #         start=start,
        #         organizer=organizer,
        #         category=category,
        #         level="Hobby/Open",
        #         link=link,
        #     ).__dict__()
        # )
        # driver.quit()

    def run_all_scrapers(self):
        # try:
        #     print("Getting data from pbt.")
        #     self.get_pbt_data()
        # except:
        #     print("Something went wrong during scrapion of PBT.")
        try:
            print("Getting data from Ladvi.")
            self.get_ladvi_data()
        except:
            print("Something went wrong during scrapion of Ladvi.")
        # try:
        #     print("Getting data from CVF.")
        #     self.get_cvf_data()
        # except:
        #     print("Something went wrong during scrapion of CVF.")

        return self.tournament_list

    def generate_json(self):
        with open("./tournaments.json", "w") as outfile:
            json.dump(self.tournament_list, outfile, ensure_ascii=False)
