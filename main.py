import requests, bs4, re, json, time
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
        
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        qselect = "SELECT * FROM macbook WHERE name=?"
        qinsert = "INSERT INTO macbook VALUES (?, ?)"
        qupdate = "UPDATE macbook SET price=? WHERE name=?"
        for key in my_json:
            # print(key)
            name = my_json[key]["NAME"]
            if name[:7] != "Ноутбук":
                continue
            price = int(my_json[key]["PRICE"])
            if cursor.execute(qselect, (name,)).fetchone():
                cursor.execute(qupdate, (price, name))
            else:
                cursor.execute(qinsert, (name, price))
        
        connection.commit()
        connection.close()




if __name__ == "__main__":
    # url = input("Enter url to search")
    url = "https://wishmaster.me/catalog/?s=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&q=macbook+air"
    my_search = Page(url)
    while True:
        my_search.update_database()
        time.sleep(1800)
    

