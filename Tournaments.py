from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time as tm
import json
import re
import requests
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, date, timedelta
from CzechMonths import CzechMonths
from Logger import CustomLogger,logging
from typing import Final
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service



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
    last_update:date

    def __init__(self, name,tournament_date, city,areal, capacity, signed, price, start, organizer, category, level, link,last_update):
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
        self.last_update = last_update
    
    def __str__(self):
        return f"Name: {self.name}\n   Date: {self.tournament_date}\n   City: {self.city}\n   Areal: {self.areal}"    
    def __repr__(self):
        return f"{self.name}"
    def __eq__(self, other):
        return (
            isinstance(other, TournamentInfo)
            and self.name == other.name
            and self.tournament_date == other.tournament_date
        )

    def __hash__(self):
        return hash((self.name,self.tournament_date))
            
class TournamentManagement():
    tournament_set:set[TournamentInfo]
    driver: webdriver
    total_found_tournaments:int
    def __init__(self):
        self.tournament_set = set()
        cl = CustomLogger()
        self.custom_log_manager = cl
        self.logger = cl.logger
        self.total_found_tournaments = 0                      

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
    def get_level_by_name(self, name):
        if name:
            name_lower = name.lower()
            if "amat" in name_lower or "kemp" in name_lower or "hobb" in name_lower or  "začát" in name_lower or "zacat" in name_lower:
                return "Hobby"
        return "Open"

    def open_chrome_with_url(self, url):
        testing = False
        try:
            if not testing:
                service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
            chrome_options = webdriver.ChromeOptions()
            if not testing:
                chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--headless")
            if not testing:
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--no-sandbox")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.implicitly_wait(10)
            self.driver.maximize_window()
            self.driver.get(url)
            return True
        except:
            self.logger.error("Open chrom with url failed.")
            return False

    def get_ladvi_data(self):
        tournament_areal = "Beachklub Ládví"
        tournament_city = "Praha"
        url = "https://beachklubladvi.cz/beachvolejbal/beach-turnaje/"
        self.custom_log_manager.log_delimiter()
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
        
        self.total_found_tournaments += number_of_tournaments
        if number_of_tournaments > 0:
            self.custom_log_manager.info_message_only(f"   Number of found tournaments: {number_of_tournaments}.\n")
        else:
            self.custom_log_manager.info_message_only(f"   No turnaments in this areal.\n")
            self.driver.quit()
            return True
            
        self.driver.quit()
        
        for tournament_id in range(number_of_tournaments):
            self.custom_log_manager.info_message_only(f"   Processing tournament {tournament_id+1}/{number_of_tournaments}")
            self.custom_log_manager.info_message_only('   Scraping...')
            
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
            
            # self.custom_log_manager.info_message_only(f"Tournament name: {tournament_name}")
            
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
                price = int(new_content.find_element(By.CLASS_NAME, "flb_event_price").text.split(",")[0])/2

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
            level = self.get_level_by_name(tournament_name)
            last_update = datetime.now()
            self.tournament_set.add(
                TournamentInfo(tournament_name,tournament_date,tournament_city,tournament_areal,capacity,signed,price,start,organizer,category,level,link,last_update)
            )
            self.driver.quit()
            self.custom_log_manager.info_message_only('   Data scraped succesfuly!')
            self.custom_log_manager.info_message_only('')
        return True
    
    def get_michalek_data(self):
        tournament_areal = "PBT Střešovice"
        tournament_city = "Praha"
        url = "https://michalek-beach.rezervuju.cz/training?event_group_id=36"
        self.custom_log_manager.log_delimiter()
        self.custom_log_manager.info_message_only(f"\nAreal: {tournament_areal} - Ondra Michálek.\n")
        
        if not self.open_chrome_with_url(url):
            return False
        
        # get tourmament elements
        try:
            tournament_elements = self.driver.find_elements(By.CLASS_NAME,"sf_admin_row")
        except:
            self.logger.error("Failed to get tourmament elements.")
            return False
        
        number_of_tournaments:int = len(tournament_elements)
        self.total_found_tournaments += number_of_tournaments
        if number_of_tournaments > 0:
            self.custom_log_manager.info_message_only(f"   Number of found tournaments: {number_of_tournaments}.\n")
        else:
            self.custom_log_manager.info_message_only(f"   No turnaments in this areal.\n")
            self.driver.quit()
            return True
        
        for tournament_id in range(number_of_tournaments):
            self.custom_log_manager.info_message_only(f"   Processing tournament {tournament_id+1}/{number_of_tournaments}")
            self.custom_log_manager.info_message_only('   Scraping...')
            
            if not self.open_chrome_with_url(url):
                continue
            
            # get information which is on main page                
            try:
                tournament_element = self.driver.find_elements(By.CLASS_NAME,"sf_admin_row")[tournament_id]
                tournament_name = tournament_element.find_element(By.CLASS_NAME,"sf_admin_list_td_name").text
                # self.custom_log_manager.info_message_only(f"   Tournament name: {tournament_name}")
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
                tm.sleep(1)
                
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
                
            level = self.get_level_by_name(tournament_name)
            organizer = "Ondřej Michálek"
            last_update = datetime.now()
            self.tournament_set.add(
                TournamentInfo(tournament_name,tournament_date,tournament_city,tournament_areal,capacity,signed,price,start,organizer,category,level,url,last_update)
            )
            self.driver.quit()
            self.custom_log_manager.info_message_only('   Data scraped succesfuly!')
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

    def get_pankrac_data(self):
        tournament_areal = "Beachklub Pankrác"
        tournament_city = "Praha"
        tournament_name = "Turnaj kempařů s Mírou Nekolou"       
        organizer = "Miroslav Nekola" 
        # urls of every category 
        urls = {
            "mix" : "https://www.beachklub.cz/turnaje/turnaj-mixy-s-mirou-nekolou",
            "men" : "https://www.beachklub.cz/turnaje/turnaj-pro-kempare",
            "women" : "https://www.beachklub.cz/turnaje/turnaj-pro-kempare-zeny"
        }
        self.custom_log_manager.log_delimiter()
        self.custom_log_manager.info_message_only(f"\nAreal: {tournament_areal}.\n")
        found_tournaments_urls = []
        
        # Get url of every single tournament in each category and append it to found_tournaments_urls list 
        for url in urls:
            if not self.open_chrome_with_url(urls[url]):
                return False
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table")))  
                tournament_elements = self.driver.find_elements(By.CLASS_NAME, "table__row")
            except:
                self.logger.error(f"Failed to get main content.")
                tm.sleep(10)
                self.driver.quit()
                return False
            
            number_of_tournaments = len(tournament_elements)
            self.total_found_tournaments += number_of_tournaments
            if number_of_tournaments > 0:
                self.custom_log_manager.info_message_only(f"   Number of found tournaments: {number_of_tournaments} in category {url}.\n")
            else:
                self.custom_log_manager.info_message_only(f"   No turnaments in category {url}.\n")
                self.driver.quit()
                return True
            
            for i in range(number_of_tournaments):
                try:
                    found_tournaments_urls.append(tournament_elements[i].find_element(By.CSS_SELECTOR, "a.table__row__data").get_attribute("href"))
                except:
                    self.logger.error(f"Failed to get tournament url.")
                    tm.sleep(10)
                    self.driver.quit()
                    return False
            self.driver.quit()
            tm.sleep(10)
        
        number_of_tournaments = len(found_tournaments_urls)
        for tournament_id in range(number_of_tournaments):
            self.custom_log_manager.info_message_only(f"   Processing tournament {tournament_id+1}/{number_of_tournaments}")
            self.custom_log_manager.info_message_only('   Scraping...')
            if not self.open_chrome_with_url(found_tournaments_urls[tournament_id]):
                return False
        
            try:
                title = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#ui-id-18"))).text  
            except:
                self.logger.error(f"Failed to get main content.")
                tm.sleep(10)
                self.driver.quit()
                return False
        
                
            try:
                capacity_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".actPlaceLeft")))
                date_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.actDesc:nth-child(2)")))
                price_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.actDesc:nth-child(4)")))
                name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#ui-id-18")))
            except:
                self.logger.error(f"Failed to get main content.")
                tm.sleep(10)
                self.driver.quit()
                return False

            _,tournament_date_str,time_str = date_element.text.split()
            tournament_date = datetime.strptime(tournament_date_str, "%d.%m.%Y")
            start = time_str.split("–")[0]
            category = self.get_category_by_name(name.text)
            level = self.get_level_by_name(name.text)
            price = int(price_element.text.split()[1])/2            
            signed, capacity = re.search(r'\d+/\d+', capacity_element.text).group(0).split("/")            
            last_update = datetime.now()
            self.tournament_set.add(
                TournamentInfo(tournament_name,tournament_date,tournament_city,tournament_areal,capacity,signed,price,start,organizer,category,level,found_tournaments_urls[tournament_id],last_update)
            )
            self.driver.quit()
            self.custom_log_manager.info_message_only('   Data scraped succesfuly!')
            self.custom_log_manager.info_message_only('')
        return True

    def get_bvsp_data(self):
        self.custom_log_manager.log_delimiter()
        self.custom_log_manager.info_message_only(f"\nArealy: BVŠP.\n")
        url = "https://api.bvsp.rezervin.app/v1/event/list?categories=19"
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = json.loads(response.text)
            number_of_tournaments = len(data)
            if number_of_tournaments > 0:
                self.custom_log_manager.info_message_only(f"   Number of found tournaments: {number_of_tournaments}.\n")
            else:
                self.custom_log_manager.info_message_only(f"   No turnaments in category {url}.\n")
                return True
            self.total_found_tournaments += number_of_tournaments
            # Access the fields for each element in the 'data' list
            for element in data['data']:
                tournament_name = element['name']
                tournament_date = datetime.strptime((element['startdate'].split("T"))[0], "%Y-%m-%d")
                start = f"{element['starttime']['h']}:{element['starttime']['i']}"
                capacity = element['capacity']
                signed = element['member_count']
                tournament_areal = element['facility_name']
                price = element['price']
                tournament_city = "Praha"
                tournament_city = "Praha"
                category = self.get_category_by_name(tournament_name)
                level = self.get_level_by_name(tournament_name)
                link = "https://bvsp.cz/dospeli/turnaje/"
                organizer = "Neznámý"
                
                last_update = datetime.now()
                self.tournament_set.add(
                    TournamentInfo(tournament_name,tournament_date,tournament_city,tournament_areal,capacity,signed,price,start,organizer,category,level,link,last_update)
                )
            self.custom_log_manager.info_message_only('   Data fetched succesfuly!')
            self.custom_log_manager.info_message_only('')
        else:
            self.custom_log_manager.info_message_only('   Failed to get data from API')
            return False
        return True

    def get_pbt_data(self):
        self.custom_log_manager.log_delimiter()
        self.custom_log_manager.info_message_only(f"\nPBT Střešovice:.\n")
        fromDate = datetime.now().strftime("%Y-%m-%d")
        toDate = (datetime.now() + timedelta(days=360)).strftime("%Y-%m-%d")
        
        url = f"http://www.praguebeachteam.cz/rest/event?fromDate={fromDate}&toDate={toDate}&types=OT"
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = json.loads(response.text)
            number_of_tournaments = len(data)
            if number_of_tournaments > 0:
                self.custom_log_manager.info_message_only(f"   Number of found tournaments: {number_of_tournaments}.\n")
            else:
                self.custom_log_manager.info_message_only(f"   No turnaments in category {url}.\n")
                return True
            self.total_found_tournaments += number_of_tournaments
            # Access the fields for each element in the 'data' list
            for element in data:
                # print(element)
                # print("=========================")
                tournament_name = element['name']
                # Extract the date string from the given format
                
                date_string = element["fromDate"].replace("__DATETIME__", "")
                # Parse the date string into a datetime object
                tournament_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=1)

                start = tournament_date.strftime("%H:%M")
                capacity = element['capacity']
                signed = len(element["bookings"])
                tournament_areal = "PBT Střešovice"
                price = element['nonMemberPrice']
                tournament_city = "Praha"
                category = self.get_category_by_name(element["category"])
                level = self.get_level_by_name(tournament_name)
                link = "https://www.praguebeachteam.cz/mobile/#/embedded/anonymous/events/tournaments"
                organizer = element["organizerName"]
                last_update = datetime.now()
                self.tournament_set.add(
                    TournamentInfo(tournament_name,tournament_date,tournament_city,tournament_areal,capacity,signed,price,start,organizer,category,level,link,last_update)
                )
            self.custom_log_manager.info_message_only('   Data fetched succesfuly!')
            self.custom_log_manager.info_message_only('')
        else:
            self.custom_log_manager.info_message_only('   Failed to get data from API')
            return False
        return True

    def run_all_scrapers(self):
        start_time = datetime.now().replace(microsecond=0)
        self.custom_log_manager.info_message_only(f"---------------------------- New update started at {start_time} -------------------------")
   
        # for attempt in range(5):
        #     if self.get_pbt_data(attempt):
        #         break 


        # Scrapers
        # self.get_cvf_data()
        self.get_ladvi_data()
        self.get_michalek_data()
        self.get_pankrac_data()
        
        # APIs
        self.get_bvsp_data()
        self.get_pbt_data()
        
        # for tour in self.tournament_set:
        #     print(tour)
        #     print()
        
        
        number_of_tournaments = len(self.tournament_set)
        self.custom_log_manager.info_message_only("------------------------------------------- SUMMARY -------------------------------------------\n")
        self.custom_log_manager.info_message_only(f"Total of found tournaments: {self.total_found_tournaments}\n") 
        self.custom_log_manager.info_message_only(f"Succesfully processed: {number_of_tournaments}\n") 
        self.custom_log_manager.info_message_only(f"Failed to process: {self.total_found_tournaments - number_of_tournaments}\n") 
        self.custom_log_manager.info_message_only(f"---------------------------- Update finished at {datetime.now().replace(microsecond=0)} ----------------------------")            
        # self.custom_log_manager.info_message_only(f"--------------------------- Next update starts at {(start_time + timedelta(hours=1)).replace(microsecond=0)} --------------------------\n")            
        self.custom_log_manager.remove_all_handlers()
        return list(self.tournament_set)

    def generate_json(self):
        with open("./tournaments.json", "w") as outfile:
            json.dump(list(self.tournament_set), outfile, ensure_ascii=False)



# if __name__ == "__main__":
#     tm = TournamentManagement()
#     tm.run_all_scrapers()
                
    # print("======================================================")
    # print("tournament_name")
    # print(tournament_name)
    # print("tournament_date")
    # print(tournament_date)
    # print("tournament_city")
    # print(tournament_city)
    # print("tournament_areal")
    # print(tournament_areal)
    # print("start")
    # print(start)
    # print("organizer")
    # print(organizer)
    # print("category")
    # print(category)
    # print("price")
    # print(price)            
    # print("capacity")
    # print(capacity)            
    # print("signed")
    # print(signed)            
    # print("link")
    # print(link)