import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from telegramBot_OtodomPL import message_new_flats_for_all_users
url = 'https://www.otodom.pl/uk/oferty/wynajem/mieszkanie/poznan?market=ALL&ownerTypeSingleSelect=ALL&distanceRadius=0&limit=1000&roomsNumber=%5BONE%2CTWO%5D&extras=%5B%5D&media=%5B%5D&locations=%5Bcities_6-1%5D&priceMax=1800&viewType=listing'


class DataBase():
    flats_list = []
    is_database_created = False

    def creating_DB(self):
        conn = sqlite3.connect('flats_db.db')
        cur = conn.cursor()
            
        cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='flats'")
        if cur.fetchone()[0] != 1 :
            cur.execute("CREATE TABLE flats (header TEXT , place TEXT, price TEXT, rooms TEXT, square TEXT, picture TEXT, link TEXT)")
            self.parse_flats()
            self.add_new_flats_to_db(self.parsed_flats_list)
        self.is_database_created = True
        
        conn.commit()
        conn.close()


    def parse_flats(self):
        self.parsed_flats_list = []

        response = requests.get(url)
        parsed_html = BeautifulSoup(response.text, 'html.parser')
        html_flats_block = parsed_html.find_all(class_='css-p74l73 es62z2j17')

        for flat in html_flats_block:
            header = flat.find(class_='css-1rhznz4 es62z2j11').text
            place = flat.find(class_='css-17o293g es62z2j9').text
            price_bs4, rooms_bs4, square_bs4 = flat.find_all(class_="css-rmqm02 eclomwz0")
            price = price_bs4.text
            rooms = rooms_bs4.text
            square = square_bs4.text
            picture = flat.find('source')['srcset']
            href = flat.find('a', href=True)['href']
            link_to_ad = f'https://www.otodom.pl{href}'
            self.parsed_flats_list.append((header,place, price, rooms, square,picture, link_to_ad))
        self.parsed_flats_list

    def check_for_new_flat(self):
        self.parse_flats()

        con = sqlite3.connect('flats_db.db')
        cur = con.cursor()
        flats_in_db_list = cur.execute("select * from flats").fetchall()
        con.commit()
        con.close()
        flats_to_add = []
        for flat in self.parsed_flats_list:
            if flat not in flats_in_db_list:
                flats_to_add.append(flat)
        if flats_to_add:
            self.add_new_flats_to_db(flats_to_add)
        flats_links_to_delete = []

        for flat in flats_in_db_list:
            if flat not in self.parsed_flats_list:
                flats_links_to_delete.append((flat[6],))

        if flats_links_to_delete:
            self.delete_old_flats_from_db(flats_links_to_delete)

    def delete_old_flats_from_db(self, links_list):
        con = sqlite3.connect('flats_db.db')
        cur = con.cursor()
        cur.executemany(f"DELETE FROM flats WHERE link=?", links_list)
        con.commit()
        con.close()


    def add_new_flats_to_db(self, flats_list):
        con = sqlite3.connect('flats_db.db')
        cur = con.cursor()
        cur.executemany("INSERT INTO flats VALUES (?, ?, ?, ?, ?, ?, ?)", flats_list)
        con.commit()
        con.close()
        
        if self.is_database_created == True:
            try:
                message_new_flats_for_all_users(flats_list)
            except Exception as e:
                print(e)
   

db = DataBase()
db.creating_DB()
while True:
    db.check_for_new_flat()
    time.sleep(10)

    

