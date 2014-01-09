from twpol.download_followers import mainDownloadFun
import random, time

if __name__ == "__main__":
    time.sleep(5*random.randint(0,10)) # that way they don't clash at start
    print "starting worker!"
    mainDownloadFun()