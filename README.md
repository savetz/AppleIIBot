# AppleIIBot

The code that runs the Atari 8-bit Twitter bot at https://twitter.com/AppleIIBot

I'm sharing this so people can use this as a stepping stone to making their own, different bots.

Documentation for using the bot is at https://appleiibot.com

The main twitter posting code is based on what I learned from "The Reply to Mentions Bot" at https://realpython.com/twitter-bot-python-tweepy/#the-config-module

Dependencies. So many dependencies:
- Tweepy. Specifically the fork that allows video uploads. https://github.com/tweepy/tweepy/pull/1414 They plan on folding that feature into the main program but as of this writing, haven't.
- The command-line version of AppleCommander. At http://applecommander.github.io and https://github.com/AppleCommander/AppleCommander
- Java, to run AppleCommander
- ffmpeg, for processing video files: https://ffmpeg.org
- and in the assets/ directory: TKTK. These are not provided in this repository due to copyright.
