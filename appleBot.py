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

        language = 0 # default to BASIC

        exp = "{\w*?L\w*(?:}|\s)" #{L
        if re.search(exp,basiccode):
            language=1 #it's LOGO
            logger.info("it's LOGO")
            if(starttime == 3):
                starttime = 0

        exp = "{\w*?T\w*(?:}|\s)" #{T
        if re.search(exp,basiccode):
            language=2 #it's Terrapin Logo
            logger.info("it's Terrapin LOGO")
            if(starttime == 3):
                starttime = 5

        #remove any { command
        exp = "{\w*(?:}|\s)" #{anything till space or }
        basiccode = re.sub(exp,'',basiccode)
        
        #whitespace
        basiccode = basiccode.strip()

        #halt if string is empty
        if not basiccode:
            logger.info("!!! basiccode string is empty, SKIPPING")
            continue;

        exp='(https?|ftp):\/\/([\da-z\.-]+)\.([a-z]{2,6})([\/\w\?\.-]*)*\/?'
        if (re.search(exp,basiccode)):
            logger.info("Ooh, its a URL to a disk image")
            if(os.path.isfile("working/BOT.dsk")):
                os.remove("working/BOT.dsk")
            result=os.system('curl -L -k -o working/BOT.dsk --max-filesize 143360 ' + basiccode)
            if(os.path.isfile("working/BOT.dsk") == False):
                logger.info("!!! DISK IMAGE FAILED, SKIPPING")
                continue
            if(os.path.getsize("working/BOT.dsk") != 143360):
                logger.info("!!! NOT DSK IMAGE SIZE, SKIPPING")
                continue
        else:
            outputFile = open('working/incomingBASIC.txt','w')

            outputFile.write(basiccode)
            outputFile.close()

            if (language==0): #basic
                logger.info("Parsing BASIC program")
                result = os.system('python3 tokenize.py working/incomingBASIC.txt working/tokenized')
                logger.info(f"Result {result}")
                if result==256:
                    logger.info("!!! PARSER FAILED, SKIPPING")
                    continue

                logger.info("Fresh disk image")
                copyfile('assets/DOS33FRESHIE.dsk','working/BOT.dsk')

                logger.info("Moving tokenized file into disk image")
                result = os.system('java -jar ac.jar -p working/BOT.dsk HELLO BAS 0x801 < working/tokenized')

                ###the following doesn't work
                if result==256:
                    logger.info("!!! APPLECOMMANDER FAILED, SKIPPING")
                    continue
            elif (language==1): #Apple LOGO
                 logger.info("Fresh Apple logo disk images")
                 copyfile('assets/apple_logo_ii.dsk','working/BOT.dsk')
                 copyfile('assets/blank-prodos.dsk','working/BOT2.dsk')

                 logger.info("Moving logo commands into disk image")
                 result = os.system('java -jar ac.jar -ptx working/BOT.dsk STARTUP TXT < working/incomingBASIC.txt')
            else: #Terrapin
                 logger.info("Fresh Terrapin logo disk images")
                 copyfile('assets/Terrapin1.dsk','working/BOT.dsk')
                 copyfile('assets/Terrapin2.dsk','working/BOT2.dsk')

                 logger.info("Moving logo commands into disk image")
                 result = os.system('java -jar ac.jar -ptx working/BOT.dsk STARTUP.LOGO TXT < working/incomingBASIC.txt')


        if green==1:
            logger.info("Fresh linapple conf file (green)")
            copyfile('assets/linapple-green.conf','linapple.conf')
        elif green==2:
            logger.info("Fresh linapple conf file (amber)")
            copyfile('assets/linapple-amber.conf','linapple.conf')
        else:
            logger.info("Fresh linapple conf file")
            copyfile('assets/linapple.conf','linapple.conf')

        logger.info("Firing up emulator")

        if (language==0):
            cmd = '/home/atari8/apple2bot/linapple -1 working/BOT.dsk'.split()
        elif (language==1):
            cmd = '/home/atari8/apple2bot/linapple -1 working/BOT.dsk -2 working/BOT2.dsk'.split()
        elif (language==2):
            cmd = '/home/atari8/apple2bot/linapple -1 working/BOT.dsk -2 working/BOT2.dsk'.split()

        emuPid = subprocess.Popen(cmd)
        logger.info(f"   Process ID {emuPid.pid}")

        if language==1: #Logo
            time.sleep(15) #time to boot before typing
            logger.info("Typing RETURN to start logo")
            os.system('xdotool search --class apple key --delay 200 Return')

        #if language==2: #Terrapin Logo
            #time.sleep(20) #time to boot before recording

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
