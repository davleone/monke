# monke

monke is a simple software to get a report on how many channel subscriptions you have amassed on Telegram.

It can be useful if you want to:
- maintain a log of the number of subscriptions beyond Telegram's statistics current time frame;
- automatically sum the numbers of subscriptions of various channel;
- automatically calculate how much each channel counts in proportion to the sum of them all.

I developed it for personal use, as I manage a little network of channels and finds it useful to see how the network as a whole is going.

# How to use monke

Download the source code using the following command: 

`$ git clone https://github.com/davleone/monke`

Then install the dependencies required:

`$ pip install -r requirements.txt`

Comments in **config.yaml** explain each setting and how editing them impacts the activity of the software. Feel free to edit the configuration file according to your needs. 

You can get your bot token by contacting [@BotFather](https://t.me/botfather). 

You can then run the software with the following command:

`$ python main.py`

In some cases (e.g. Linux cronjob) you might find useful to specify the absolute path of the config.yaml file in main.py; you can easily do so by modifying the corresponding strings.

## How it works

A number of channels are listed in a watchlist with their IDs. 
The software - either at a schedule time or on request - will generate a report on the channels in the watchlist.  The report should look like this:

> Total subscription count: 48975
>
> \- @biblonet - 47248 (96.47%)\
> \- @biblonet_en - 1304 (2.66%)\
> \- @biblonet_es - 423 (0.86%)

A report is generated:
- (when do_polling is set to False) By launching the software with `$ python main.py`
- (when do_polling is set to True) By giving the command /count to the bot or at the scheduled hour

When do_polling is set to True the software will remain active and answer to message received on Telegram. Some functions will only be available to the specified admin.
You might simply forward a message from a given channel to have that channel added to the watchlist. Even if you don't want to add a channel this way, please notice that for how Telegram currently works you might need to forward a message from the specified channel (or add the bot to it), otherwise it won't be able to call the getChat method and retrieve data.

The software does not log any report or maintain any of the retried data in a database. As the reports are sent over Telegram, however, they are supposed to remain available there. 

# Contributing 

You can help by: 
- **providing bug reports** (with as much information as possible, such as your CONFIG.yaml and your log files);
- **share your ideas** on how to improve the software;
- **updating and correcting** the documentation;
- **sending a pull request**.

If you need to customize this software for some very specific purpose, I recommend forking it.

## Versioning conventions

We follow a simple _Major.Minor.Patch_ convention.

A major release is one that requires a change in the config.yaml file.
A minor release is one that adds new features to the software without requiring any change to the config.yaml file.
A patch release is one that does nor adds new features nor requires changes to the config.yaml file.