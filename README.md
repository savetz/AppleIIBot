# AppleIIBot
 The code that runs the Apple II Twitter bot at https://twitter.com/AppleIIBot

I'm sharing this so people can use this as a stepping stone to making their own, different bots.

Documentation for using the bot is at https://appleiibot.com

The main twitter posting code is based on what I learned from "The Reply to Mentions Bot" at https://realpython.com/twitter-bot-python-tweepy/#the-config-module

New version 2 Aug 2021 adds:
- run Apple Logo II code by using the {L} directive
- run Terrapin Logo PLUS code by using the {T} directive
- download and run any arbitrary DSK file from the web by including a URL (and nothing else) in the tweet. This doesn't work super reliably and not really what I want to do with the bot. I'll probably take it out in the future.

Dependencies. So many dependencies:
- A Twitter account, and API keys for it https://developer.twitter.com/en/products/twitter-api
- Tweepy. Specifically the fork that allows video uploads. https://github.com/tweepy/tweepy/pull/1414 They plan on folding that feature into the main program but as of this writing, haven't.
- LinApple, an Apple II emulator for linux. https://github.com/linappleii/linapple. I'm using a version that's built for Raspberry Pi. Maybe it's this: https://github.com/dabonetn/linapple-pie or maybe it's this: https://wiki.reactivemicro.com/Linapple_Raspberrypi *shrug*
- The command-line version of AppleCommander. At http://applecommander.github.io and https://github.com/AppleCommander/AppleCommander
- Java, to run AppleCommander
- bastoken, a tokenizer for AppleSoft BASIC created specially for this project by KrisKennaway: https://github.com/KrisKennaway/bastoken. The bot expects it to be named tokenize.py.
- ffmpeg, for processing video files: https://ffmpeg.org
- in the assets/ directory: an Apple II DOS 3.3 DSK image confugured to run HELLO at boot, called DOS33FRESHIE.dsk
- in the assets/ directory: a blank ProDOS DSK image, called PRODOSFRESHIE.dsk
- in the assets/ directory, Apple Logo II disk image called apple_logo_ii.dsk. Not provided here because copyright, but it's not hard to find.
- in the assets/ directory, Terrapin Logo PLUS v1.2 Language Disk, named Terrapin1.dsk, and the Utilities Disk, named Terrapin2.dsk. Also not provided here because copyright.
- an X Virtual Frame Buffer running on display 98 (/usr/bin/Xvfb :98 -ac -screen 0 1024x768x24)
