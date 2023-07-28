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

bot_user = bot.get_me()


# Commands
@bot.message_handler(commands=["start", "hello"])
def handle_start_hello(message: str):
    if (message.chat.type == "group" or message.chat.type == "supergroup"
            or message.chat.type == "channel"):
        if message.text.__contains__(f"@{bot_user.username}"):
            bot.reply_to(message=message,
                         text="Hi! Here are things you can do:")
            bot.send_message(
                chat_id=message.chat.id,
                text="type /transfers to see the transfer informations"
            )
            bot.send_message(
                chat_id=message.chat.id,
                text="type /matchfixtures to see the match results"
            )
    else:
        bot.reply_to(message=message,
                     text="Hi! Here are things you can do:")
        bot.send_message(
            chat_id=message.chat.id,
            text="type /transfers to see the transfer informations"
        )
        bot.send_message(
            chat_id=message.chat.id,
            text="type /matchfixtures to see the match results"
        )


@bot.message_handler(commands=["transfers"])
def handle_transfers(message: str):
    if (message.chat.type == "group" or message.chat.type == "supergroup"
            or message.chat.type == "channel"):
        if message.text.__contains__(f"@{bot_user.username}"):
            markup = select_date_template()

            bot.send_message(chat_id=message.chat.id,
                             text="Select date?",
                             reply_markup=markup)
    else:
        markup = select_date_template()

        bot.send_message(chat_id=message.chat.id,
                         text="Select date?",
                         reply_markup=markup)


@bot.message_handler(commands=["matchfixtures"])
def handle_match_fixtures(message: str):
    if (message.chat.type == "group" or message.chat.type == "supergroup"
            or message.chat.type == "channel"):
        if message.text.__contains__(f"@{bot_user.username}"):
            markup = fixture_template()

            bot.send_message(
                chat_id=message.chat.id,
                text="Choose one of these below",
                reply_markup=markup)
    else:
        markup = fixture_template()

        bot.send_message(
            message.chat.id, "Choose one of these below", reply_markup=markup)


# Markup Templates
def select_date_template():
    markup = types.InlineKeyboardMarkup()

    today = types.InlineKeyboardButton("today", callback_data="0")
    yesterday = types.InlineKeyboardButton("yesterday", callback_data="1")
    day_3_from_now = types.InlineKeyboardButton(
        (date.today() - timedelta(days=2)).strftime("%d-%m-%Y"),
        callback_data="2"
    )
    day_4_from_now = types.InlineKeyboardButton(
        (date.today() - timedelta(days=3)).strftime("%d-%m-%Y"),
        callback_data="3"
    )
    day_5_from_now = types.InlineKeyboardButton(
        (date.today() - timedelta(days=4)).strftime("%d-%m-%Y"),
        callback_data="4"
    )
    day_6_from_now = types.InlineKeyboardButton(
        (date.today() - timedelta(days=5)).strftime("%d-%m-%Y"),
        callback_data="5"
    )
    markup.row(today, yesterday, day_3_from_now)
    markup.row(day_4_from_now, day_5_from_now, day_6_from_now)

    return markup


def select_type_template(num_day_from_now: int):
    markup = types.InlineKeyboardMarkup()

    all = types.InlineKeyboardButton(
        "All", callback_data=f"full-{num_day_from_now}")
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

    return markup


def fixture_template():
    markup = types.InlineKeyboardMarkup()

    top10 = types.InlineKeyboardButton("Top 25", callback_data="Top 25")
    top25 = types.InlineKeyboardButton("Top 50", callback_data="Top 50")
    top50 = types.InlineKeyboardButton("Top 100", callback_data="Top 100")
    england = types.InlineKeyboardButton("England", callback_data="England")
    spain = types.InlineKeyboardButton("Spain", callback_data="Spain")
    italy = types.InlineKeyboardButton("Italy", callback_data="Italy")
    germany = types.InlineKeyboardButton("Germany", callback_data="Germany")
    france = types.InlineKeyboardButton("France", callback_data="France")
    netherlands = types.InlineKeyboardButton(
        "Netherlands", callback_data="Netherlands")
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
    womaneuro = types.InlineKeyboardButton(
        "Women's Euro", callback_data="Women's Euro")
    maneuro = types.InlineKeyboardButton(
        "Man's Euro", callback_data="Man's Euro")

    markup.row(top10, top25, top50)
    markup.row(england, spain, italy)
    markup.row(germany, france, netherlands)
    markup.row(championleague, europaleague, womanworldcup)
    markup.row(manworldcup, womaneuro, maneuro)

    return markup


# Callback handler
@bot.callback_query_handler(lambda query: query.data in
                            ["0", "1", "2", "3", "4", "5"])
def handle_select_type(query: str):
    num_day_from_now: int = int(query.data)

    markup = select_type_template(num_day_from_now)

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="What type then?",
        reply_markup=markup,
    )


@bot.callback_query_handler(lambda query: query.data == "back-to-select-date")
def handle_back_to_select_date(query: str):
    markup = select_date_template()

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Select date?",
        reply_markup=markup,
    )


@bot.callback_query_handler(
    lambda query: re.match("(full|majorc|toptrans)-.", query.data)
)
def handle_get_transfers(query: str):
    type: str = query.data.split("-")[0]
    full_type: str = (
        "All" if type == "full" else (
            "Major league" if type == "majorc" else "Top")
    )
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
    today = (date.today() - timedelta(days=num_day_from_now)
             ).strftime('%d-%m-%Y')
    if len(results) == 0:
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text="No transfer",
        )
    else:
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=f"{full_type} transfers in {today}:",
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
                f"to {result['destination']} {result['amount']} \n \n"
            )

            if len(text_message) > 3000:
                list_text_message.append(text_message)
                text_message = ""
        list_text_message.append(text_message)

        for text_message in list_text_message:
            bot.send_message(query.message.chat.id, text_message)


@bot.callback_query_handler(
    lambda query: query.data
    in [
        "Top 25",
        "Top 50",
        "Top 100",
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
def handle_group_fixtures(query: str):
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="processing... please wait",
        reply_markup=None,
    )

    results: list = get_all_fixtures(date.today().strftime("%Y%m%d"))

    if query.data == "Top 25":
        results: pd.DataFrame = results.head(25)
    elif query.data == "Top 50":
        results: pd.DataFrame = results.head(50)
    elif query.data == "Top 100":
        results: pd.DataFrame = results.head(100)
    else:
        results: pd.DataFrame = results.loc[results["league"] == query.data]

    group_by_league: pd.DataFrame = results.groupby("league", sort=False)

    list_text_message: list = []
    text_message: str = ""
    if len(results) == 0:
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text="No fixture today",
        )
    else:
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=f"Today {query.data} fixtures",
        )

        for league, results in group_by_league:
            text_message += f"\n{str(league)}\n"
            group_by_type: pd.DataFrame = results.groupby("type", sort=False)

            for type, results in group_by_type:
                text_message += f"      {str(type)} \n"

                for _, result in results.iterrows():
                    if result["status"] == "NS":
                        text_message += f"{result['start_time']}:   {result['home_team']} - {result['away_team']}\n"
                    elif result["status"] == "AP":
                        text_message += f"{result['status']}:   {result['home_team']} {result['home_score_all']}({result['home_score_pen']})-{result['away_score_all']}({result['away_score_pen']}) {result['away_team']}\n"
                    else:
                        text_message += f"{result['status']}:   {result['home_team']} {result['home_score_all']}-{result['away_score_all']} {result['away_team']}\n"
            if len(text_message) > 3000:
                list_text_message.append(text_message)
                text_message = ""

        list_text_message.append(text_message)

        for text_message in list_text_message:
            bot.send_message(query.message.chat.id, text_message)


# Polling
bot.infinity_polling()
