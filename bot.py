import os
import telebot
import re
from telebot import types
from dotenv import load_dotenv
from datetime import date, timedelta
import pandas as pd

from get_transfers import get_all_transfers
from get_fixtures import get_all_fixtures


load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)


# Commands
@bot.message_handler(commands=["start", "hello"])
def handle_start_hello(message: str):
    bot.reply_to(message, "Hi! Here are things you can do:")
    bot.send_message(
        message.chat.id, "type /transfers to see the transfer informations"
    )
    bot.send_message(message.chat.id, "type /matchfixtures to see the match results")


@bot.message_handler(commands=["transfers"])
def handle_transfers(message: str):
    markup = transfer_template()

    bot.send_message(message.chat.id, "Select date?", reply_markup=markup)

@bot.message_handler(commands=["matchfixtures"])
def handle_match_fixtures(message: str):
    markup = fixture_template()

    bot.send_message(message.chat.id, "Choose one of these below", reply_markup=markup)


# Markup Templates
def transfer_template():
    markup = types.InlineKeyboardMarkup()

    today = types.InlineKeyboardButton("today", callback_data="0")
    yesterday = types.InlineKeyboardButton("yesterday", callback_data="1")
    day_3_from_now = types.InlineKeyboardButton(
        (date.today() - timedelta(days=2)).strftime("%d-%m-%Y"), callback_data="2"
    )
    day_4_from_now = types.InlineKeyboardButton(
        (date.today() - timedelta(days=3)).strftime("%d-%m-%Y"), callback_data="3"
    )
    day_5_from_now = types.InlineKeyboardButton(
        (date.today() - timedelta(days=4)).strftime("%d-%m-%Y"), callback_data="4"
    )
    day_6_from_now = types.InlineKeyboardButton(
        (date.today() - timedelta(days=5)).strftime("%d-%m-%Y"), callback_data="5"
    )
    markup.row(today, yesterday, day_3_from_now)
    markup.row(day_4_from_now, day_5_from_now, day_6_from_now)

    return markup


def fixture_template():
    markup = types.InlineKeyboardMarkup()

    top10 = types.InlineKeyboardButton("Top 10", callback_data="Top 10")
    top25 = types.InlineKeyboardButton("Top 25", callback_data="Top 25")
    top50 = types.InlineKeyboardButton("Top 50", callback_data="Top 50")
    england = types.InlineKeyboardButton("England", callback_data="England")
    spain = types.InlineKeyboardButton("Spain", callback_data="Spain")
    italy = types.InlineKeyboardButton("Italy", callback_data="Italy")
    germany = types.InlineKeyboardButton("Germany", callback_data="Germany")
    france = types.InlineKeyboardButton("France", callback_data="France")
    netherlands = types.InlineKeyboardButton("Netherlands", callback_data="Netherlands")
    championleague = types.InlineKeyboardButton(
        "Champion League", callback_data="Champion League"
    )
    europaleague = types.InlineKeyboardButton(
        "Europa League", callback_data="Europa League"
    )
    womanworldcup = types.InlineKeyboardButton(
        "Women's World Cup", callback_data="Women's World Cup"
    )
    manworldcup = types.InlineKeyboardButton(
        "Man's World Cup", callback_data="Man's World Cup"
    )
    womaneuro = types.InlineKeyboardButton("Women's Euro", callback_data="Women's Euro")
    maneuro = types.InlineKeyboardButton("Man's Euro", callback_data="Man's Euro")

    markup.row(top10, top25, top50)
    markup.row(england, spain, italy)
    markup.row(germany, france, netherlands)
    markup.row(championleague, europaleague, womanworldcup)
    markup.row(manworldcup, womaneuro, maneuro)

    return markup



# Callback handler
@bot.callback_query_handler(lambda query: query.data in ["0", "1", "2", "3", "4", "5"])
def handle_selected_date(query: str):
    num_day_from_now: int = int(query.data)

    markup = types.InlineKeyboardMarkup()

    all = types.InlineKeyboardButton("All", callback_data=f"full-{num_day_from_now}")
    major = types.InlineKeyboardButton(
        "Major league", callback_data=f"majorc-{num_day_from_now}"
    )
    toptrans = types.InlineKeyboardButton(
        "Top transfer", callback_data=f"toptrans-{num_day_from_now}"
    )
    back = types.InlineKeyboardButton(
        "<< Back to date select", callback_data="back-to-select-date"
    )

    markup.row(all, major)
    markup.row(toptrans, back)

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="What type then?",
        reply_markup=markup,
    )


@bot.callback_query_handler(lambda query: query.data == "back-to-select-date")
def handle_back_to_select_date(query: str):
    markup = transfer_template()

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Choose the day?",
        reply_markup=markup,
    )


@bot.callback_query_handler(
    lambda query: re.match("(full|majorc|toptrans)-.", query.data)
)
def handle_type(query: str):
    type: str = query.data.split("-")[0]
    num_day_from_now: int = int(query.data.split("-")[1])

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="processing... please wait",
        reply_markup=None,
    )

    results: list = get_all_transfers(num_day_from_now, type)

    list_text_message: list = []
    text_message: str = ""
    if len(results) == 0:
        bot.send_message(query.message.chat.id, "No transfer")
    else:
        bot.send_message(
            query.message.chat.id, "Transfers in selected date:"
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

            if len(text_message) > 4000:
                list_text_message.append(text_message)
                text_message = ""
        list_text_message.append(text_message)

        for text_message in list_text_message:
            bot.send_message(query.message.chat.id, text_message)


@bot.callback_query_handler(
    lambda query: query.data
    in [
        "Top 10",
        "Top 25",
        "Top 50",
        "England",
        "Spain",
        "Italy",
        "Germany",
        "France",
        "Netherlands",
        "Champion League",
        "Women's World Cup",
        "Man's World Cup",
        "Women's Euro",
        "Man's Euro",
    ]
)
def handle_group_fixture(query: str):
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="processing... please wait",
        reply_markup=None,
    )

    results: list = get_all_fixtures(date.today().strftime("%Y%m%d"))

    if query.data == "Top 10":
        results: pd.DataFrame = results.head(10)
    elif query.data == "Top 25":
        results: pd.DataFrame = results.head(25)
    elif query.data == "Top 50":
        results: pd.DataFrame = results.head(50)
    else:
        results: pd.DataFrame = results.loc[results["league"] == query.data]

    group_by_league: pd.DataFrame = results.groupby("league")

    list_text_message: list = []
    text_message: str = ""
    if len(results) == 0:
        bot.send_message(query.message.chat.id, "No fixture today")
    else:
        for league, results in group_by_league:
            text_message += f"\n{str(league)} \n"
            group_by_type: pd.DataFrame = results.groupby("type")

            for type, results in group_by_type:
                text_message += f"{str(type)} \n"

                for _, result in results.iterrows():
                    if result["status"] == "NS":
                        text_message += f"{result['start_time']}:   {result['home_team']} - {result['away_team']}\n"
                    elif result["status"] == "AP":
                        text_message += f"{result['status']}:   {result['home_team']} {result['home_score_all']}({result['home_score_pen']})-{result['away_score_all']}({result['away_score_pen']}) {result['away_team']}\n"
                    else:
                        text_message += f"{result['status']}:   {result['home_team']} {result['home_score_all']}-{result['away_score_all']} {result['away_team']}\n"
            if len(text_message) > 4000:
                list_text_message.append(text_message)
                text_message = ""

        list_text_message.append(text_message)

        for text_message in list_text_message:
            bot.send_message(query.message.chat.id, text_message)


# Polling
bot.infinity_polling()
