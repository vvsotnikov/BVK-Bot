import json
import logging
import os

import requests
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)


# TODO: add docstrings
def get_volume():
    response = json.loads(requests.get(volumeRequest).content)
    # TODO: handle situations when answer['Error'] is not None
    return f"Объем торгов в BTC: {response['VolumeBTC']}\n" \
           f"Объем торгов в USD: {response['VolumeUSD']}"


def get_tickers():
    response = json.loads(requests.get(tickerRequest).content)
    # TODO: handle situations when answer['Error'] is not None
    return f"Цена последней сделки: {response['Tickers'][0]['Last'] * 100000000} сатоши\n" \
           f"Ордеры на продажу от {response['Tickers'][0]['LowPrice'] * 100000000} сатоши\n" \
           f"Ордеры на покупку от {response['Tickers'][0]['HighPrice'] * 100000000} сатоши\n" \
           f"Изменение курса за сутки: {response['Tickers'][0]['PercentChange']}%"


def shout_five():
    return 'ПЯТЬ ТЫЩ!!! FIVE THOUSAND!!!'


chooses_dict = {'volume': get_volume,
                'ticker': get_tickers,
                'FIVE': shout_five}


def start(bot, update):
    update.message.reply_text(
        'Привет! Я -  Бот Биткоина Пять Тыщ. Я могу поделиться с тобой иннформацией о торгах на бирже или крикнуть'
        '"ПЯТЬ ТЫЩ!" Возможно, когда-нибудь ты сможешь покупать и продавать Биткоин Пять Тыщ с моей помощью ;)\n'
        'Hi! My name is Bitcoin Five Thousand Bot. I can provide you real-time information about BVK market or just '
        'shout "FIVE THOUSAND!!!', reply_markup=markup)
    logger.info(f'User {update.message.from_user} started the conversation.')


# TODO: implement separate handlers for each request
def answer(bot, update):
    text = update.message.text
    for key in chooses_dict.keys():
        if key in text:
            update.message.reply_text(chooses_dict[key]())
            return CHOOSING
    update.message.reply_text('Некорректный запрос! Incorrect request!')
    return RESPONSE


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Бот выключен. Bot is disabled',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("cancel", cancel))
    dp.add_handler(MessageHandler(Filters.text, answer))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    token = os.environ.get('BVK_TOKEN')
    if token is None:
        token = open('token.txt', 'r').read()
    assert token is not None, logger.warning('CAN NOT RETRIEVE TOKEN!')

    volumeRequest = 'https://api.crex24.com/CryptoExchangeService/BotPublic/Return24Volume?request=[NamePairs=BTC_BVK]'
    tickerRequest = 'https://api.crex24.com/CryptoExchangeService/BotPublic/ReturnTicker?request=[NamePairs=BTC_BVK]'

    CHOOSING, RESPONSE = range(2)
    reply_keyboard = [['Текущий курс / Current ticker',
                       'Объем торгов / Market volume',
                       'ПЯТЬ ТЫЩ!!! / FIVE THOUSAND!!!']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    main()
