from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time as tm
import json
import re
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, date, timedelta
from CzechMonths import CzechMonths
from Logger import CustomLogger,logging

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

    def __init__(self, name,tournament_date, city,areal, capacity, signed, price, start, organizer, category, level, link):
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
        
class TournamentManagement():
    tournament_list:list[TournamentInfo]
    def __init__(self):
        self.tournament_list = []
        cl = CustomLogger()
        self.custom_log_manager = cl
        self.logger = cl.logger
        
    def get_category_by_name(self, name):
        if name:
            name_lower = name.lower()
            if "mix" in name_lower:
                return "Mixy"
            elif "muz" in name_lower or "muž" in name_lower:
                return "Muži"
            elif "zen" in name_lower or "žen" in name_lower:
                return "Ženy"
        self.logger.warning("Did not find category in tournament name.")
        return "Jiné"

    def open_chrome_with_url(self, url):
        try:
            self.driver_options = webdriver.ChromeOptions()
            self.driver_options.add_argument("--headless")
            self.driver = webdriver.Chrome(options=self.driver_options)
            self.driver.implicitly_wait(10)
            self.driver.maximize_window()
            self.driver.get(url)
            return True
        except:
            self.logger.error("Open chrom with url failed.")
            return False
            
    def get_pbt_data(self):
        tournament_areal = "Prague Beach Team (Střešovice)"
        tournament_city = "Praha"
        url = "https://www.praguebeachteam.cz/mobile/#/embedded/anonymous/events/tournaments"
        self.open_chrome_with_url(url)
        main_content = self.driver.find_element(By.CLASS_NAME, "event-list-container")
        tm.sleep(3)
        print("checkpoint 1")
        days = main_content.find_elements(By.CSS_SELECTOR, "ul.list-group")
        tm.sleep(3)
        print("checkpoint 2")
        for day in days:
            wait = WebDriverWait(self.driver, 10)
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
            wait = WebDriverWait(self.driver, 10)
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

            self.driver.back()

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
        self.driver.quit()

    def get_ladvi_data(self):
        tournament_areal = "Beachklub Ládví"
        tournament_city = "Praha"
        url = "https://beachklubladvi.cz/beachvolejbal/beach-turnaje/"
        
        self.custom_log_manager.info_message_only(f"\nAreal: {tournament_areal}.\n")
        
        if not self.open_chrome_with_url(url):
            return False
        
        try:
            tournament_table = self.driver.find_element(By.ID, "turnaj_flb_event_list")
        except:
            self.logger.error("Table with tournaments was not found.")
            return False
        
        try:
            number_of_tournaments = len(tournament_table.find_elements(By.CLASS_NAME, "flb_event_list_item"))
        except:
            self.logger.error("Failed to get number of tournaments.")
            return False
        
        if number_of_tournaments > 0:
            self.custom_log_manager.info_message_only(f"Number of found tournaments: {number_of_tournaments}.\n")
        else:
            self.custom_log_manager.info_message_only(f"No turnaments in this areal.\n")
            
        self.driver.quit()
        
        for tournament_id in range(number_of_tournaments):
            self.custom_log_manager.info_message_only(f"Processing tournament {tournament_id+1}/{number_of_tournaments}")
            
            if not self.open_chrome_with_url(url):
                continue    
            
            try:
                tournament_table = self.driver.find_element(By.ID, "turnaj_flb_event_list")
            except:
                self.logger.error("Table with tournaments was not found.")
                continue
            
            try:
                tournament_table.find_elements(By.CLASS_NAME, "flb_event_list_item_button_detail")[tournament_id].click()
            except:
                self.logger.error("Failed to get tournament detail button.")
                continue
                
            tm.sleep(3)

            try:
                new_content = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "flb_event_detail")))
            except:
                self.logger.error("Failed to get tournament details.")
                continue
            try:
                tournament_name = new_content.find_element(By.CLASS_NAME, "flb_event_name").text
            except:
                self.logger.error("Failed to get tournament name.")
                continue
            
            self.custom_log_manager.info_message_only(f"Tournament name: {tournament_name}")
            self.custom_log_manager.info_message_only('Scraping...')
            
            try:
                tournament_date_str, start = new_content.find_element(By.CLASS_NAME, "flb_event_start").text.split(" ")
            except:
                self.logger.error("Failed to get tournament date and start time.")
                continue

            tournament_date = datetime.strptime(tournament_date_str, "%d.%m.%Y")

            try:
                organizer = (new_content.find_element(By.CLASS_NAME, "flb_event_organiser")
                                        .find_element(By.CLASS_NAME, "fullname").text)
            except:
                self.logger.error("Failed to get tournament organizer name.")
                continue

            try:
                price = new_content.find_element(By.CLASS_NAME, "flb_event_price").text.split(",")[0]

                capacity, free = list(map(int,re.findall(r"\d+",new_content.find_element(By.CLASS_NAME, "flb_event_places").text,),))
            except:
                self.logger.error("Failed to get tournament price and capacity.")
                continue
            
            signed = int(capacity) - int(free)

            try:
                link = self.driver.current_url
            except:
                self.logger.error("Failed to get tournament url.")
                continue
            
            category = self.get_category_by_name(tournament_name)

            self.tournament_list.append(
                TournamentInfo(tournament_name,tournament_date,tournament_city,tournament_areal,capacity,signed,price,start,organizer,category,"Hobby/Open",link,)
            )
            self.driver.quit()
            self.custom_log_manager.info_message_only('Data scraped succesfuly!')
            self.custom_log_manager.info_message_only('')
        return True
    
    def get_michalek_data(self):
        tournament_areal = "Prague Beach Team (Střešovice)"
        tournament_city = "Praha"
        url = "https://michalek-beach.rezervuju.cz/training?event_group_id=36"
        self.custom_log_manager.log_delimiter()
        self.custom_log_manager.info_message_only(f"\nAreal: {tournament_areal}.\n")
        
        if not self.open_chrome_with_url(url):
            return False
        
        # get tourmament elements
        try:
            tournament_elements = self.driver.find_elements(By.CLASS_NAME,"sf_admin_row")
        except:
            self.logger.error("Failed to get tourmament elements.")
            return False
        
        number_of_tournaments:int = len(tournament_elements)
        
        for tournament_id in range(number_of_tournaments):
            self.custom_log_manager.info_message_only(f"Processing tournament {tournament_id+1}/{number_of_tournaments}")
            
            if not self.open_chrome_with_url(url):
                continue
            
            # get information which is on main page                
            try:
                tournament_element = self.driver.find_elements(By.CLASS_NAME,"sf_admin_row")[tournament_id]
                tournament_name = tournament_element.find_element(By.CLASS_NAME,"sf_admin_list_td_name").text
                self.custom_log_manager.info_message_only(f"Tournament name: {tournament_name}")
                self.custom_log_manager.info_message_only('Scraping...')
                day,month,year = tournament_element.find_element(By.CLASS_NAME,"sf_admin_list_td_date").text.split(" ")
                tournament_date_str = f"{day}{CzechMonths(month).to_number()}.{year}"
                tournament_date = datetime.strptime(tournament_date_str, "%d.%m.%Y")
                capacity,signed = tournament_element.find_element(By.CLASS_NAME,"sf_admin_list_td_capacity_with_participations_count").text.split('/')

            except:
                self.logger.error("Failed to get info from main page.")
                continue            
            
            # open detail of tournament
            try:
                self.driver.find_elements(By.CLASS_NAME,"sf_admin_row")[tournament_id].find_element(By.CLASS_NAME,"sf_admin_action_detail").click() 
                tm.sleep(3)
                
                detail_description = self.driver.find_element(By.CLASS_NAME,"event_perex").text.lower()

                category = self.get_category_by_name(tournament_name)

                price_match = re.search(r'startovné (\d+)', detail_description)
                price = "0"
                if price_match:
                    price = price_match.group().split(" ")[1]

                start_match = re.search(r'začátek (\d+:\d+)', detail_description)
                start = "0"
                if start_match:
                    start = start_match.group().split(" ")[1]
            except:
                self.logger.error("Failed to get info after clicking tournament detail.")
                continue
                
            organizer = "Ondřej Michálek"
            self.tournament_list.append(
                TournamentInfo(tournament_name,tournament_date,tournament_city,tournament_areal,capacity,signed,price,start,organizer,category,"Hobby/Open",url,)
            )
            self.driver.quit()
            self.custom_log_manager.info_message_only('Data scraped succesfuly!')
            self.custom_log_manager.info_message_only('')
            
        return True

    def get_cvf_data(self):
        tournament_areal = "Beachklub Ládví"
        tournament_city = "Praha"
        url_muzi = (
            "https://www.cvf.cz/beach/turnaje/?rok=2023&mesic=&kategorie=Muži&slozka="
        )
        url_zeny = (
            "https://www.cvf.cz/beach/turnaje/?rok=2023&mesic=&kategorie=Ženy&slozka="
        )
        self.open_chrome_with_url(url_muzi)
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
        start_time = datetime.now().replace(microsecond=0)
        self.custom_log_manager.info_message_only(f"---------------------------- New update started at {start_time} -------------------------")
   
        # self.get_pbt_data()
        # self.get_cvf_data()
        self.get_ladvi_data()
        self.get_michalek_data()
            
        self.custom_log_manager.info_message_only("------------------------------------------- SUMMARY -------------------------------------------\n")
        self.custom_log_manager.info_message_only("TBD\n") 
        self.custom_log_manager.info_message_only(f"---------------------------- Update finished at {datetime.now().replace(microsecond=0)} ----------------------------")            
        # self.custom_log_manager.info_message_only(f"--------------------------- Next update starts at {(start_time + timedelta(hours=1)).replace(microsecond=0)} --------------------------\n")            
        self.custom_log_manager.remove_all_handlers()
        return self.tournament_list

    def generate_json(self):
        with open("./tournaments.json", "w") as outfile:
            json.dump(self.tournament_list, outfile, ensure_ascii=False)
