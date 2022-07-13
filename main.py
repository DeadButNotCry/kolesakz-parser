
from email import message
import math
from time import sleep
from bs4 import BeautifulSoup
import requests
import re
import sets
pattern = "https://m.kolesa.kz"
list = [""]


def send_to_tg(text):
    send_text = 'https://api.telegram.org/bot' + sets.bot_token + \
        '/sendMessage?chat_id=' + sets.bot_chatID + '&parse_mode=HTML&text=' + text
    requests.get(send_text)


def main(city, user_percent):
    text = requests.get("https://m.kolesa.kz/hot/cars/").text
    bs = BeautifulSoup(text, "lxml")
    cars = bs.find_all(class_="search-list__item")
    last_car = cars[0]
    a = last_car.find("a")
    if (a is not None) and (list[0] != a["href"]):
        href = a["href"]
        message_text = pattern+href+"\n"
        print(pattern+href)
        list[0] = href
        # TODO: add city check
        region = a.find(class_="a-card-info__region").text.strip().lower()
        if city.lower() in region:  # city.lower() in region
            car_text = requests.get(pattern+href).text
            car_bs = BeautifulSoup(car_text, "lxml")

            properties_div = car_bs.find(class_="a-block a-properties")
            properties_list = properties_div.find_all(
                class_="a-properties__info")
            for i in properties_list:
                values = i.find_all("div")
                message_text += "<b>"+values[0].text.strip()+"</b> " + \
                    values[1].text.strip()+"\n"

            if "<b>Растаможен в Казахстане</b> Да" in message_text:
                notes_block = car_bs.find(class_="a-block a-notes")
                if notes_block is not None:
                    notes = notes_block.find_all("p")
                for i in notes:
                    text_note = re.sub(" +", " ", i.text).replace("\n", "")
                    message_text += text_note+"\n"
                price_info = requests.get(
                    "https://m.kolesa.kz/a/average-price/"+href.split("/")[-1]).json()
                if not "error_code" in price_info:
                    message_text = "<b>" + \
                        price_info["data"]["name"] + \
                        "</b>" + "\n"+message_text + "\n"

                    percent = price_info["data"]["diffInPercents"]
                    if percent <= 0 and abs(percent) >= user_percent:
                        message_text += "<b> Дешевле на " + str(price_info["data"]["averagePrice"]-price_info["data"]
                                                                ["currentPrice"]) + " T или на " + str(abs(percent)) + "% </b>"
                        send_to_tg(message_text)


if __name__ == "__main__":
    city = input("Введите город: ")
    percent = float(input("На сколько процентов машина должна быть дешевле: "))
    while True:
        main(city, percent)
        sleep(10)
        print("parsing")
