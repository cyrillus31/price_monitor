import requests, bs4, re, json, time, os
import sqlite3

pattern = r"(?<=var offers = ){.+}(?=;)"

class Page:
    def __init__(self, url):
        self.url = url

    def update_database(self):
        response = requests.get(self.url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        # return soup.find_all(class_="product-card__content-price") 
        # return soup.find_all(class_="product-card")[1].find_all(class_="product-card__content-price") 
        # return soup.find_all("text/javascript")
        search = response.text
        myjson_string = re.findall(pattern, search)[0]
        my_json = json.loads(myjson_string)
        # print(my_json)
        
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        qselect = "SELECT name, price, discount, quantity FROM macbook WHERE name=?"
        qinsert = "INSERT INTO macbook VALUES (?, ?, ?, ?)"
        qupdate = "UPDATE macbook SET price=?, discount=? WHERE name=?"
        for key in my_json:
            # print(key)
            name = my_json[key]["NAME"]
            if name[:7] != "Ноутбук":
                continue
            price = int(my_json[key]["PRICE"])
            quantity = int(my_json[key]["QUANTITY"])
            discount = int(my_json[key]["DISCOUNT"])
            fetch = cursor.execute(qselect, (name,)).fetchone()
            if fetch[1] != price or fetch[2] != discount or fetch[3] != quantity:
                cursor.execute(qupdate, (price, discount, name))
                self.is_updated = True
            else:
                cursor.execute(qinsert, (name, price, discount, quantity))
        
        connection.commit()
        connection.close()
    
    def get_table():
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        get_table = "SELECT name, price, discount, quantity FROM macbook"
        all_rows = cursor.execute(get_table).fetchall()



TOKEN = os.getenv("PRICE_MONITOR_TELEBOT_TOKEN")
CHAT_ID = 617762423

def sending_updates(token, is_updated: bool, chat_id) -> None:
    if is_updated:
        url = "https://api.telegram.org/bot" + token
        method = "/getUpdates"
        r = requests.get(url+method)
        print(r.content)



if __name__ == "__main__":
    # url = input("Enter url to search")
    url = "https://wishmaster.me/catalog/?s=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&q=macbook+air"
    my_search = Page(url)
    while True:
        my_search.update_database()
        # time.sleep(1800)
        # time.sleep(3)
        sending_updates(TOKEN, True, CHAT_ID)
        break
    

