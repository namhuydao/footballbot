import os
import telebot
from telebot import types
from datetime import date, datetime, timedelta
from get_transfers import get_all_transfers
from get_fixtures import get_all_fixtures


TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "hello"])
def handle_start_hello(message):
    bot.reply_to(message, "Hi! Here are things you can do:")
    bot.send_message(
        message.chat.id, "type /transfers to see the transfer informations")
    bot.send_message(
        message.chat.id, "type /matchfixtures to see the match results")


@bot.message_handler(commands=["transfers"])
def handle_transfers(message):
    markup = types.ReplyKeyboardMarkup()

    today = types.KeyboardButton("today")
    yesterday = types.KeyboardButton("yesterday")
    day_3_from_now = types.KeyboardButton(
        (date.today() - timedelta(days=2)).strftime("%d-%m-%Y")
    )
    day_4_from_now = types.KeyboardButton(
        (date.today() - timedelta(days=3)).strftime("%d-%m-%Y")
    )
    day_5_from_now = types.KeyboardButton(
        (date.today() - timedelta(days=4)).strftime("%d-%m-%Y")
    )
    day_6_from_now = types.KeyboardButton(
        (date.today() - timedelta(days=5)).strftime("%d-%m-%Y")
    )
    markup.row(today, yesterday, day_3_from_now)
    markup.row(day_4_from_now, day_5_from_now, day_6_from_now)
    send_msg = bot.send_message(
        message.chat.id, "Choose the day?", reply_markup=markup)
    bot.register_next_step_handler(send_msg, handle_selected_date)


def handle_selected_date(message):
    selected_date = message.text
    if selected_date == "today":
        num_day_from_now = 0
    elif selected_date == "yesterday":
        num_day_from_now = 1
    else:
        num_day_from_now = (
            date.today() - datetime.strptime(selected_date, "%d-%m-%Y").date()
        ).days

    markup = types.ReplyKeyboardMarkup()

    all = types.KeyboardButton("All")
    major = types.KeyboardButton("Major league")
    toptrans = types.KeyboardButton("Top transfer")

    markup.row(all, major, toptrans)
    send_msg = bot.send_message(
        message.chat.id, "What type then?", reply_markup=markup)
    bot.register_next_step_handler(send_msg, handle_type, num_day_from_now)


def handle_type(message, num_day_from_now):
    type = message.text

    bot.send_message(
        message.chat.id,
        text="processing... please wait",
        reply_markup=telebot.types.ReplyKeyboardRemove(),
    )

    results = get_all_transfers(num_day_from_now, type)

    text_message = ""
    if len(results) == 0:
        bot.send_message(message.chat.id, "No transfer happening yet")
    else:
        bot.send_message(
            message.chat.id, "Here are some transfer that happening this day:"
        )

        for _, result in results.iterrows():
            if result["start"] == "Free":
                result["start"] = "free agent"
            if result["destination"] == "Free":
                result["destination"] = "be free agent"
            if result["amount"] is None or result["amount"] == "":
                result["amount"] = ""
            else:
                result["amount"] = "for " + result["amount"]

            text_message += (
                f"{result['player_name']} from {result['start']} "
                f"to {result['destination']} {result['amount']} \n"
            )
        bot.send_message(message.chat.id, text_message)


@bot.message_handler(commands=["matchfixtures"])
def handle_match_fixtures(message):
    markup = types.ReplyKeyboardMarkup()

    top10 = types.KeyboardButton("Top 10")
    top25 = types.KeyboardButton("Top 25")
    top50 = types.KeyboardButton("Top 50")
    england = types.KeyboardButton("England")
    spain = types.KeyboardButton("Spain")
    italy = types.KeyboardButton("Italy")
    germany = types.KeyboardButton("Germany")
    france = types.KeyboardButton("France")
    netherlands = types.KeyboardButton("Netherlands")
    championleague = types.KeyboardButton("Champion League")
    europaleague = types.KeyboardButton("Europa League")
    womanworldcup = types.KeyboardButton("Women's World Cup")
    manworldcup = types.KeyboardButton("Man's World Cup")
    womaneuro = types.KeyboardButton("Women's Euro")
    maneuro = types.KeyboardButton("Man's Euro")

    markup.row(top10, top25, top50)
    markup.row(england, spain, italy)
    markup.row(germany, france, netherlands)
    markup.row(championleague, europaleague, womanworldcup)
    markup.row(manworldcup, womaneuro, maneuro)

    send_msg = bot.send_message(
        message.chat.id, "Choose one of these below", reply_markup=markup
    )
    bot.register_next_step_handler(send_msg, handle_group_fixture)


def handle_group_fixture(message):
    bot.send_message(
        message.chat.id,
        text="processing... please wait",
        reply_markup=telebot.types.ReplyKeyboardRemove(),
    )

    results = get_all_fixtures(date.today().strftime("%Y%m%d"))

    if message.text == "Top 10":
        results = results.head(10)
    elif message.text == "Top 25":
        results = results.head(25)
    elif message.text == "Top 50":
        results = results.head(50)
    else:
        results = results.loc[results["league"] == message.text]

    group_by_league = results.groupby("league")

    text_message = ""
    if len(results) == 0:
        bot.send_message(message.chat.id, "No fixture today")
    else:
        for league, results in group_by_league:
            text_message += f"\n{str(league)} \n"
            group_by_type = results.groupby("type")

            for type, results in group_by_type:
                text_message += f"{str(type)} \n"

                for _, result in results.iterrows():
                    if result["status"] == "NS":
                        text_message += f"{result['start_time']}:   {result['home_team']} - {result['away_team']}\n"
                    elif result['status'] == 'AP':
                        text_message += f"{result['status']}:   {result['home_team']} {result['home_score_all']}({result['home_score_pen']})-{result['away_score_all']}({result['away_score_pen']}) {result['away_team']}\n"
                    else:
                        text_message += f"{result['status']}:   {result['home_team']} {result['home_score_all']}-{result['away_score_all']} {result['away_team']}\n"

    bot.send_message(message.chat.id, text_message)


bot.infinity_polling()
