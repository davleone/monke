""" Distributed under GNU Affero GPL.

    monke 2.0b 10/02/2022

    Copyright (C) 2019 - 2022 Davide Leone

    You can contact me at leonedavide[at]protonmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>."""

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
import logging
import yaml
import html
import time


def main():
    """
    This function is used to generate the report and send it to the target chat. The software get data for every and
    each channel in the watchlist (specified in CONFIG.yaml). In the report each channel is represented with a
    line, like " - @biblonet_en - 1304 (2.66%)" If the channel is private (therefore has no username), the software
    will use the channel title instead of the username; it will also try to format the title with the invite link to
    the private channel. As the channel title can contain any kind of character, it is sterilized using the
    html.escape() function.
    The software is able to calculate how much each channel weights, in percentage, for the total subscriptions count.
    To do so, the software needs to first calculate the total count by processing all the data and then generate each
    line of the message. This explains why the software uses two "for" cycles instead of just one.
    Under some reasonable assumption, we should expect to limit on characters for a message to not be a problem; even
    with a watchlist of 100 channels. Therefore the report is sent in a single big message.
    """

    logging.info('main function called')

    report = ''
    channels_members = []
    channels_name = []
    total_count = 0

    for channel in id_channels:
        try:
            logging.debug('The following ID is being processed: {}'.format(channel))
            channel_info = updater.bot.getChat(channel, 100)
            channel_members = updater.bot.get_chat_member_count(channel, 100)

            if 'username' in list(channel_info.to_dict()):
                channel_name = '@' + channel_info.username
            else:
                if channel_info.invite_link is None:
                    channel_name = html.escape(channel_info.title[:33])
                else:
                    channel_name = "<a href='" + channel_info.invite_link + "'>" \
                                   + html.escape(channel_info.title[:33]) + "</a> "

            logging.debug('Subscribers counted: {} Channel name: {}'.format(channel_members, channel_name))
            channels_members.append(channel_members)
            channels_name.append(channel_name)
            total_count += channel_members

        except:
            logging.warning('An error occurred while analyzing channel {}'.format(channel))

    if show_percentage is True:
        for x in range(len(channels_name)):
            report += " - {} - {} ({}%)\n".format(channels_name[x], channels_members[x],
                                                  round(100 * (channels_members[x] / total_count), 2))
    else:
        for x in range(len(channels_name)):
            report += " - {} - {}\n".format(channels_name[x], channels_members[x])

    report = '{} {}\n\n'.format(messages_text['total_count'], total_count) + report

    logging.debug('The main function has generated the report')

    updater.bot.sendMessage(
        chat_id=id_target_chat,
        text=report,
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    text='Source code',
                    url=source_url
                )
            ]]
        )
    )


def start_callback(update, context):
    """
    This function is used to answer to /start, /help and /info commands by providing a simple welcome message.
    """
    logging.info('start_callback function called')

    update.message.reply_text(
        text=messages_text['welcome'],
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    text='Source code',
                    url=source_url
                )
            ]]
        )
    )


def count_callback(update, context):
    """
    This function is used to call the main function when the command /count is received from the admin.
    This allows the admin to activate the main function whenever he/she wants.
    """
    logging.info('count_callback function called')

    update.message.reply_text(
        text=messages_text['count_command'],
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    text='Source code',
                    url=source_url
                )
            ]]
        )
    )

    main()


def add_channel_callback(update, context):
    """
    This function is used to add a new channel to the watchlist. It is called when a forwarded message is received from
    the admin. A number of if/else statement are used to process the data received and give him/her the best feedback.
    If an ID is to be added to the watchlist it is simply appended at the end of the CONFIG.yaml file, when the
    id_channels list is located. The variable on which the software operates is also updated.
    The reply_to_message_id is used in case a lot of forwarded messages are received; this way the admin can easily
    understand how each message has been processed.
    The {id} keyboard is used in certain cases so that the admin can link any channel with the IDs in the watchlist.
    """

    logging.info('add_channel_callback function called')

    if update.message.forward_from_chat.type == 'channel':
        id_new_channel = update.message.forward_from_chat.id

        if id_new_channel not in id_channels:
            with open('config.yaml', 'a') as fo:
                fo.write('\n  - {}'.format(id_new_channel))

            id_channels.append(id_new_channel)

            if update.message.forward_from_chat.username is None:
                update.message.reply_text(messages_text['warning_private'].format(**{'id': id_new_channel}),
                                          reply_to_message_id=update.message.message_id,
                                          parse_mode='HTML')
            else:
                update.message.reply_text(messages_text['added_success'].format(**{'id': id_new_channel}),
                                          reply_to_message_id=update.message.message_id,
                                          parse_mode='HTML')

        else:
            update.message.reply_text(messages_text['error_already_listed'].format(**{'id': id_new_channel}),
                                      reply_to_message_id=update.message.message_id, parse_mode='HTML')

    else:
        update.message.reply_text(messages_text['error_not_a_channel'], reply_to_message_id=update.message.message_id,
                                  parse_mode='HTML')


with open('config.yaml') as file:
    # If needed, 'config.yaml' should be changed to the absolute path for this file
    config = yaml.safe_load(file)

do_polling = config['do_polling']  # Type: bool
id_channels = config['id_channels']  # Type: list of int
if id_channels is None:  # The watchlist is empty
    id_channels = []
id_admin = config['id_admin']  # Type: int or str
id_target_chat = config['id_target_chat']  # Type: int or str
log_filename = config['log_filename']  # Type: str
logging_level = config['logging_level']  # Type: str
messages_text = config['messages_text']  # Type: list of str
send_at_hour = config['send_at_hour']  # Type: int
show_percentage = config['show_percentage']  # Type: bool
source_url = config['source_url']  # Type: str
token = config['token']  # Type: str

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=log_filename,
                    level=logging_level,
                    filemode='w')

updater = Updater(token=token)

if do_polling:
    """
    If do_polling is set to True the software is supposed to remain active. 
    The bot is prepared to receive and process messages from Telegram, and then prepares to call the main function at
    the specified hour - as this call can be scheduled in the CONFIG.yaml file. 
    The software is designed to activate to allow only one scheduled main call per day, as we do not expect users to
    need anymore than that and, in exceptional cases, the /count command can be used.
    If an invalid hour is set, the software will not be checking the time for the scheduled call.
    """

    updater.dispatcher.add_handler(
        CommandHandler(
            command=['start', 'help', 'info'],
            callback=start_callback,
            filters=Filters.chat_type.private
        ))

    if str(id_admin).isdigit():
        allow_only_admin = Filters.chat(chat_id=id_admin)
    else:
        allow_only_admin = Filters.chat(username=id_admin)

    updater.dispatcher.add_handler(
        CommandHandler(command='count', callback=count_callback, filters=allow_only_admin & Filters.chat_type.private)
    )

    updater.dispatcher.add_handler(
        MessageHandler(
            filters=Filters.forwarded & allow_only_admin & Filters.chat_type.private,
            callback=add_channel_callback))

    updater.start_polling()

    while True:

        if (send_at_hour < 0) | (send_at_hour > 24):
            break

        elif time.localtime().tm_hour == send_at_hour:
            logging.info('The main function is being called at the scheduled hour')
            main()
            time.sleep(82800)

        elif time.localtime().tm_hour > send_at_hour:
            time.sleep(60 * 60 * (24 - time.localtime().tm_hour))

        else:
            time.sleep(
                60 * 60 * (send_at_hour - 1 - time.localtime().tm_hour) +
                60 * (60 - time.localtime().tm_min)
            )

else:  # The software should now execute the main function and then stop
    main()
