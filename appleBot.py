#AppleIIBot by @KaySavetz. 2020-2021.

import tweepy
import logging
from botConfig import create_api
import time
from shutil import copyfile
import os,sys
import subprocess
from datetime import datetime
from unidecode import unidecode
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id, tweet_mode='extended').items():
        new_since_id = max(tweet.id, new_since_id)

        logger.info(f"Tweet from {tweet.user.name}")

        #remove @ mentions, leaving just the BASIC code
        basiccode = re.sub('^(@.+?\s)+','',tweet.full_text)

        basiccode = unidecode(basiccode)

        #unescape >, <, and &
        basiccode = basiccode.replace("&lt;", "<")
        basiccode = basiccode.replace("&gt;", ">")
        basiccode = basiccode.replace("&amp;", "&")

        #look for start time command
        exp = "{\w*?B(\d\d?)\w*(?:}|\s)" # {B\d\d  B= Begin
        result = re.search(exp,basiccode)
        if result:  
            starttime = int(result.group(1))
            logger.info(f" Requests start at {starttime} seconds")
        else:
            starttime = 3

        #look for length of time to record command
        exp = "{\w*?S(\d\d?)\w*(?:}|\s)" # {S\d\d  S= Seconds to record
        result=re.search(exp,basiccode)
        if result:
            recordtime = int(result.group(1))
            logger.info(f" Requests record for {recordtime} seconds")
        else:
            recordtime = 30
        if recordtime <1:
            recordtime=1

        green=0    #default is color

        exp = "{\w*?G\w*(?:}|\s)" #{G
        if re.search(exp,basiccode):
            green=1 #greenscreen
            logger.info("requests green screen")
        
        exp = "{\w*?A\w*(?:}|\s)" #{A
        if re.search(exp,basiccode):
            green=2 #amberscreen
            logger.info("requests amber screen")

        #remove any { command
        exp = "{\w*(?:}|\s)" #{anything till space or }
        basiccode = re.sub(exp,'',basiccode)
        
        #whitespace
        basiccode = basiccode.strip()

        #halt if string is empty
        if not basiccode:
            logger.info("!!! basiccode string is empty, SKIPPING")
            continue;

        outputFile = open('working/incomingBASIC.txt','w')

        outputFile.write(basiccode)
        outputFile.close()

        logger.info("Parsing program")
        result = os.system('python3 tokenize.py working/incomingBASIC.txt working/tokenized')
        logger.info(f"Result {result}")
        if result==256:
            logger.info("!!! PARSER FAILED, SKIPPING")
            continue

        logger.info("Fresh disk image")
        copyfile('assets/DOS33FRESHIE.dsk','working/BOT.dsk')

        if green==1:
            logger.info("Fresh linapple conf file (green)")
            copyfile('assets/linapple-green.conf','linapple.conf')
        elif green==2:
            logger.info("Fresh linapple conf file (amber)")
            copyfile('assets/linapple-amber.conf','linapple.conf')
        else:
            logger.info("Fresh linapple conf file")
            copyfile('assets/linapple.conf','linapple.conf')

        logger.info("Moving tokenized file into disk image")
        #result = os.system('java -jar ac.jar -p working/BOT.dsk HELLO < working/tokenized')
        result = os.system('java -jar ac.jar -p working/BOT.dsk HELLO BAS 0x801 < working/tokenized')

        ###the following doesn't work
        if result==256:
            logger.info("!!! APPLECOMMANDER FAILED, SKIPPING")
            continue

        logger.info("Firing up emulator")

        cmd = '/home/atari8/apple2bot/linapple -1 working/BOT.dsk'.split()

        emuPid = subprocess.Popen(cmd)
        logger.info(f"   Process ID {emuPid.pid}")

        time.sleep(starttime)

        logger.info("Recording with ffmpeg")
        result = os.system(f'/usr/bin/ffmpeg -y -hide_banner -loglevel warning -draw_mouse 0 -f x11grab -r 30 -video_size 850x630 -i :98+100,70 -q:v 0 -pix_fmt yuv422p -t {recordtime} working/APPLE_BIG.mp4')

        logger.info("Stopping emulator")
        emuPid.kill()

        logger.info("Converting video")
        result = os.system('ffmpeg -loglevel warning -y -i working/APPLE_BIG.mp4 -vcodec libx264 -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -pix_fmt yuv420p -strict experimental -r 30 -t 2:20 -acodec aac -vb 1024k -minrate 1024k -maxrate 1024k -bufsize 1024k -ar 44100 -ac 2 working/APPLE_SMALL.mp4')
        #per https://gist.github.com/nikhan/26ddd9c4e99bbf209dd7#gistcomment-3232972

        logger.info("Uploading video")  

        media = api.media_upload("working/APPLE_SMALL.mp4")

        logger.info(f"Media ID is {media.media_id}")

        time.sleep(5)
#TODO replace with get_media_upload_status per https://github.com/tweepy/tweepy/pull/1414

        logger.info(f"Posting tweet to @{tweet.user.screen_name}")
        tweettext = f"@{tweet.user.screen_name} "
        post_result = api.update_status(auto_populate_reply_metadata=False, status=tweettext, media_ids=[media.media_id], in_reply_to_status_id=tweet.id)

        logger.info("Done!")

    return new_since_id

def main():
    os.chdir('/home/atari8/apple2bot/')

    api = create_api()

    now = datetime.now()
    logger.info("START TIME:")
    logger.info(now.strftime("%Y %m %d %H:%M:%S")) 

    try:
        sinceFile = open('sinceFile.txt','r')
        since_id = sinceFile.read()
    except:
        sinceFile = open('sinceFile.txt','w')
        sinceFile.write("1")
        logger.info("created new sinceFile")
        since_id = 1

    sinceFile.close()       
    since_id = int(since_id)
    logger.info(f"Starting since_id {since_id}")
    
    os.environ["DISPLAY"] = ":98"

    while True:
        didatweet=0
        new_since_id = check_mentions(api, since_id)

        if new_since_id != since_id:
            since_id = new_since_id
            logger.info(f"Since_id now {since_id}")
        
            sinceFile = open('sinceFile.txt','w')
            sinceFile.write(str(since_id))
            sinceFile.close()
            didatweet=1

        if didatweet==0:
            logger.info("Waiting...")
            time.sleep(120)

if __name__ == "__main__":
    main()
    
