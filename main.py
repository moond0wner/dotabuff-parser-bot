import telebot
import pyshorteners
import requests
from bs4 import BeautifulSoup

s = pyshorteners.Shortener()
token = '7081478178:AAEGHhoYz2QQ15g-p7g_GsUt0YuYfVX1Zd0'
bot = telebot.TeleBot(token)
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'}

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id,"Привет я бот который получает информацию о аккаунте, герое из Дота 2 с помощью DotaBuff.")
    bot.send_message(message.chat.id, "Список команд:"
                                      "\n/start - Запустить бота, список команд."
                                      "\n/get_profile - Получить информацию о профиле (никнейм, кол-во игры, победы, поражения, ранг."
                                      #"\n/get_heroes_list - Получить (полную или неполную) информацию о героях на этом аккаунте.")

@bot.message_handler(commands=['get_profile'])
def handle_profile(message):
    bot.send_message(message.chat.id, "Отправь мне айди аккаунта и я дам тебе информацию о нем")

    def get_account(message):
        try:
            id = str(message.text)
            player_profile_url = 'https://www.dotabuff.com/players/' + id
            # Отправляем запрос на сайт
            response = requests.get(player_profile_url, headers=header)

            # Используем BeautifulSoup для парсинга HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            profile_table1 = soup.find('div', class_='header-content-secondary')
            rows = profile_table1.find_all('dl')

            # ник
            nick = soup.find('div', class_='header-content-title').get_text()
            for i in nick:
                if "Overview" in nick:
                    nick = nick.replace('Overview', '')

            # ранг
            rank = soup.find('div', class_='rank-tier-wrapper')['title'].split(': ')[1]

            for row in rows:
                cols = profile_table1.find_all('dd')
                last_game = cols[0].text.strip()  # последняя игра
                stats = cols[1].text.split('-')  # победы-поражения-покинуты. Собираем в список и раскидываем по переменным
                winrate = cols[2].text.strip()  # винрейт аккаунта

                wins = stats[0].strip() # победы
                losses = stats[1].strip() # поражения
                abandons = stats[2].strip() # покинуты

            # общее кол-во матчей
            all_matches = int(wins) + int(losses) + int(abandons)

            # аватарка аккаунта
            avatar_element = soup.find('div', class_='header-content-avatar')
            avatar_url = avatar_element.find("img")["src"]
            avatar_url = s.tinyurl.short(avatar_url)

            bot.send_message(message.chat.id, f'Результат: '
                                              f'\nНикнейм: {nick}'
                                              f'\nРанг: {rank}'
                                              f'\nВинрейт: {winrate}'
                                              f'\nПоследний матч: {last_game}'
                                              f'\nПобеды: {wins}'
                                              f'\nПоражения: {losses}'
                                              f'\nПокинуты: {abandons}'
                                              f'\nКоличество матчей: {all_matches}'
                                              f'\nАватарка: \n{avatar_url}')
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка: {e}')



    bot.register_next_step_handler(message, get_account)
