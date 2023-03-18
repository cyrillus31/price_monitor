import requests, bs4, re, json, time, os, logging, io
from datetime import datetime as dt
import sqlite3
import db

logging.basicConfig(filename="price_monitor.log", format="%(asctime)s :: %(message)s", encoding="UTF-8", level=logging.DEBUG)
pattern = r"(?<=var offers = ){.+}(?=;)"

class Page:
    def __init__(self, url):
        self.url = url
        self.is_updated = True

    def update_database(self):
        response = requests.get(self.url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        # return soup.find_all(class_="product-card__content-price") 
        # return soup.find_all(class_="product-card")[1].find_all(class_="product-card__content-price") 
        # return soup.find_all("text/javascript")
        search = response.text
        myjson_string = re.findall(pattern, search)[0]
        my_json = json.loads(myjson_string)
        # logging.debug(my_json)
        
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        qselect = "SELECT name, price, discount, quantity FROM macbook WHERE name=?"
        qinsert = "INSERT INTO macbook VALUES (?, ?, ?, ?)"
        qupdate = "UPDATE macbook SET price=?, discount=?, quantity=? WHERE name=?"
        for key in my_json:
            # logging.debug(key)
            name = my_json[key]["NAME"]
            if name[:7] != "Ноутбук":
                continue
            price = int(my_json[key]["PRICE"])
            quantity = int(my_json[key]["QUANTITY"])
            discount = int(my_json[key]["DISCOUNT"])
            fetch = cursor.execute(qselect, (name,)).fetchone()
            if fetch == None:
                cursor.execute(qinsert, (name, price, discount, quantity))
                self.is_updated = True

            elif fetch[1] != price or fetch[2] != discount or fetch[3] != quantity:
                cursor.execute(qupdate, (price, discount, quantity, name))
                self.is_updated = True
        
        connection.commit()
        connection.close()
    
    def get_table(self):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        get_table = "SELECT name, price, discount, quantity FROM macbook WHERE price<150000 AND quantity>0 ORDER BY name ASC"
        all_rows = cursor.execute(get_table).fetchall()
        message = "" 
        for row in all_rows:
            message += "{}\n*PRICE: {} руб.    DISCOUNT: {}     QUANTITY: {}*\n\n".format(row[0], str(row[1]), str(row[2]), str(row[3]))
        # logging.debug(message)
        return message.replace("&quot;", " ")
            


TOKEN = os.getenv("PRICE_MONITOR_TELEBOT_TOKEN")
CHAT_ID = os.getenv("PRICE_MONITOR_TELEBOT_CHAT_ID")

def sending_updates(token, is_updated: bool, chat_id, message: str) -> None:
    url = "https://api.telegram.org/bot" + token
    method = "/sendMessage?chat_id={}&parse_mode=markdown&disable_notification={}&text={}".format(chat_id, str(not is_updated), message)
    r = requests.get(url+method)
    if r.status_code == 200:
        pass
        # logging.debug("success")
        # logging.debug(r.content)
    else:
        pass
        # logging.debug("a problem occured", r.status_code)
        # logging.debug(r.content)

def check(t1, t2) -> str:
    linenumber = 0
    rows1 = {}
    difference = "" 

    for row in t1.readlines():
        linenumber += 1
        rows1[linenumber] = row
        
    linenumber = 0
    rows2 = {}
    for row in t2.readlines():
        linenumber += 1
        rows2[linenumber] = row

    for linenumber in rows1:
        if rows1[linenumber] == rows2[linenumber]:
            continue
        else:
            difference += (rows1[linenumber]+rows2[linenumber]+"\n")
    return difference


if __name__ == "__main__":
    # url = input("Enter url to search")
    url = "https://wishmaster.me/catalog/?s=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&q=macbook+air"
    my_search = Page(url)
    while True:
        current_time = str(dt.now()) + "\n"
        prev_message = my_search.get_table()
        my_search.update_database()
        message = my_search.get_table()
        sending_updates(TOKEN, my_search.is_updated, CHAT_ID, current_time+message)
        if message == prev_message:
            sending_updates(TOKEN, my_search.is_updated, CHAT_ID, "NO CHANGES")
        else:
            sending_updates(TOKEN, my_search.is_updated, CHAT_ID, "THE DIFFERENCE:\n"+check(io.StringIO(prev_message), io.StringIO(message)))
            prev_message = message

        my_search.is_updated = False
        time.sleep(1500)
    

