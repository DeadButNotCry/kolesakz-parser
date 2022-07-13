
from email import message
from bs4 import BeautifulSoup
import requests
import re
import sets
pattern = "https://m.kolesa.kz"
list = [""]


def send_to_tg(text):
    send_text = 'https://api.telegram.org/bot' + sets.bot_token + '/sendMessage?chat_id=' + sets.bot_chatID + '&parse_mode=HTML&text=' + text
    requests.get(send_text)


def main(city):
    text = requests.get("https://m.kolesa.kz/hot/cars/").text
    bs = BeautifulSoup(text, "lxml")
    cars = bs.find_all(class_="search-list__item")
    last_car = cars[0]
    a = last_car.find("a")
    if (a is not None) and (list[0] != a["href"]):
        href = a["href"]
        message_text = pattern+href+"\n"
        list[0] = href
        # TODO: add city check
        region = a.find(class_="a-card-info__region").text.strip().lower()
        car_text = requests.get(pattern+href).text
        car_bs = BeautifulSoup(car_text, "lxml")

        properties_div = car_bs.find(class_="a-block a-properties")
        properties_list = properties_div.find_all(class_="a-properties__info")
        for i in properties_list:
            values = i.find_all("div")
            message_text += values[0].text.strip()+" " + \
                values[1].text.strip()+"\n"

        if "Растаможен в Казахстане Да" in message_text:
            notes = car_bs.find(class_="a-block a-notes").find_all("p")
            for i in notes:
                text_note = re.sub(" +", " ", i.text).replace("\n", "")
                message_text += text_note+"\n"
            price_info = requests.get(
                "https://m.kolesa.kz/a/average-price/"+href.split("/")[-1]).json()
            message_text = price_info["data"]["name"] + "\n"+message_text + "\n" + "Разница в процентах: " + str(price_info["data"]["diffInPercents"])
            send_to_tg(message_text)


if __name__ == "__main__":
    main("check")
