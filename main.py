import json
import logging

import requests
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)

token = open('token.txt', 'r').read()

url = f'https://api.telegram.org/bot{token}/'
volumeRequest = 'https://api.crex24.com/CryptoExchangeService/BotPublic/Return24Volume?request=[NamePairs=BTC_BVK]'
tickerRequest = 'https://api.crex24.com/CryptoExchangeService/BotPublic/ReturnTicker?request=[NamePairs=BTC_BVK]'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CHOOSING, RESPONSE = range(2)
reply_keyboard = [['Текущий курс / Current ticker',
                       'Объем торгов / Market volume',
                       'ПЯТЬ ТЫЩ!!! / FIVE THOUSAND!!!']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


# TODO: add docstrings
def get_volume():
    response = json.loads(requests.get(volumeRequest))
    # TODO: handle situations when response['Error'] is not None
    return {'BTC': response['VolumeBTC'],
            'USD': response['VolumeUSD']}


def get_tickers():
    response = json.loads(requests.get(tickerRequest))
    # TODO: handle situations when response['Error'] is not None
    return {'Last': response['Last'] * 100000000,
            'LowPrice': response['LowPrice'] * 100000000,
            'HighPrice': response['LowPrice'] * 100000000,
            'PercentChange': response['PercentChange'], }


def shout_five():
    logger.info('ПЯТЬ ТЫЩ!!! FIVE THOUSAND!!!')


chooses_dict = {'volume': get_volume,
                'ticker': get_tickers,
                'FIVE': shout_five}


def start(bot, update):
    update.message.reply_text(
        'Привет! Я -  Бот Биткоина Пять Тыщ. Я могу поделиться с тобой иннформацией о торгах на бирже или крикнуть'
        '"ПЯТЬ ТЫЩ!" Возможно, когда-нибудь ты сможешь покупать и продавать Биткоин Пять Тыщ с моей помощью ;)'
        'Hi! My name is Bitcoin Five Thousand Bot. I can provide you real-time information about BVK market or just '
        'shout "FIVE THOUSAND!!!',
        reply_markup=markup)
    return CHOOSING


def choice(bot, update):
    update.message.reply_text('Что мне сдедать?\nWhat do you want?')
    return RESPONSE


# TODO: implement separate state for each request
def response(bot, update):
    text = update.message.text
    for key in chooses_dict.keys():
        if key in text:
            chooses_dict[key]()
            return CHOOSING
    logger.info('Некорректный запрос! Incorrect request!')
    return CHOOSING


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
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
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^(ticker|volume|FIVE)$', choice)],
            RESPONSE: [MessageHandler(Filters.text, response)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
