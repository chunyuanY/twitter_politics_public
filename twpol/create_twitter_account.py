# decaptcha credentials
unm="jurnsfangers"
p="firenze"

# twitter registration info
TWITTER_ACCOUNT_USERNAME = "nryl"
TWITTER_ACCOUNT_EMAIL_END = "@mailinator.com"
TWITTER_ACCOUNT_PASSWORD = "Durpy100"
TWITTER_ACCOUNT_NAME = "Samantha Yamwood"
TWITTER_APP_NAME = "Data Yamwood"
TWITTER_APP_DESCRIPTION = "Yamwood candidates get researched."
TWITTER_APP_WEBSITE = "http://lovegov.com"
TWITTER_IPBAN_DECAY = 1500  # number of seconds until ipban wears off

CLOG = {
    "proxy_logs" : {},
    "current_driver": None,
}

import deathbycaptcha
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import *
from longscript import monitor_script
import os, json, time
from twpol.settings import PROJECT_PATH
from twpol.settings import GLOBAL
from time import sleep
import urllib
import pdb
import functools
import simplejson
from twpol.twitter_accounts import refreshTwitterAccounts
import random
import string
from longscript.models import saveSleep, saveSpecialError
import datetime

def solveCaptcha(captcha_file_name, timeout=60):
    # Put your DBC account username and password here.
    # Use deathbycaptcha.HttpClient for HTTP API.
    client = deathbycaptcha.SocketClient(unm, p)
    try:
        balance = client.get_balance()
        print "balance: " + str(balance)

        # Put your CAPTCHA file name or file-like object, and optional
        # solving timeout (in seconds) here:
        captcha = client.decode(captcha_file_name, timeout)
        if captcha:
            # The CAPTCHA was solved; captcha["captcha"] item holds its
            # numeric ID, and captcha["text"] item its text.
            print "CAPTCHA %s solved: %s" % (captcha["captcha"], captcha["text"])
            return captcha['text']
            #
            # if ...:  # check if the CAPTCHA was incorrectly solved
            #     client.report(captcha["captcha"])
    except deathbycaptcha.AccessDeniedException:
        raise
        # Access to DBC API denied, check your credentials and/or balance

# choose a random proxy, with more successfuly proxies weighted higher
def getRandomProxy():
    proxies_file_path = os.path.join(PROJECT_PATH, "ninja.txt")
    proxies_file = open(proxies_file_path, "r")
    proxies = []
    for line in proxies_file:
        proxy = line.replace("\n", "")
        proxies.append(proxy)
    final_choice = False
    while not final_choice:
        a_proxy = random.choice(proxies)
        if a_proxy == "none":
            a_proxy = ""
        proxy_stats = getProxyStats(a_proxy)
        proxy_attempts = proxy_stats["successes"] + proxy_stats["failures"] + 1
        time_since_last_blacklist = time.time() - proxy_stats["blacklisted"]
        # if blacklisted choose another one
        if time_since_last_blacklist < TWITTER_IPBAN_DECAY:
            break
        # if it has broken 4 times in a row with 0 successes, then skip it
        if proxy_stats["broken"] >= 4 and proxy_stats["successes"] == 0:
            break
        # probabilistic selection, the higher the failure percentage the more often we skip it
        skip_percentage = proxy_stats["failures"] / float(proxy_attempts)
        if random.random() > skip_percentage:
            final_choice = a_proxy
    return final_choice

def getProxyStats(proxy_string):
    proxy_stats = CLOG["proxy_logs"].setdefault(proxy_string, {"successes":0,"failures":0,"blacklisted":0,"broken":0})
    return proxy_stats

# returns a proxied web driver
def getWebDriver(proxy_string=None):
    # control group is no proxy
    if not proxy_string:
        fp = webdriver.FirefoxProfile()
        proxy = Proxy({
            'proxyType': ProxyType.DIRECT
            #'httpProxy': '',
            #'ftpProxy': '',
            #'sslProxy': '',
            #'noProxy': '' # set this value as desired
        })
        to_return = webdriver.Firefox(firefox_profile=fp, proxy=proxy)
    else:
        CLOG['current_proxy'] = proxy_string
        proxy_stats = getProxyStats(proxy_string)
        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': proxy_string,
            'ftpProxy': proxy_string,
            'sslProxy': proxy_string,
            'noProxy': '' # set this value as desired
        })
        fp = webdriver.FirefoxProfile()
        fp.set_preference("webdriver.load.strategy", "unstable")
        driver = webdriver.Firefox(firefox_profile=fp, proxy=proxy, timeout=120)
        driver.set_page_load_timeout(120)
        # for remote
        # caps = webdriver.DesiredCapabilities.FIREFOX
        # proxy.add_to_capabilities(caps)
        # driver = webdriver.Remote(desired_capabilities=caps)
        to_return = driver
    CLOG["current_driver"] = to_return # in global variable keep track of the driver, so we can close it if we need to
    return to_return

# reconnect to vpn to get new ip address ## DEPRECATED
def reconnectToVPN():
    sleep(20)

# wrapper for create twitter account which increases wait time before next attempt if their are multiple failures in a row
def createTwitterAccountWrapper(this_account_num):
    print("%TT%: " + str(time.time()))
    current_proxy = CLOG.get("current_proxy")
    if not current_proxy: CLOG["current_proxy"] = current_proxy = getRandomProxy()
    try:
        if GLOBAL.get('script_sleep') > 10:
            CLOG["current_proxy"] = current_proxy = getRandomProxy()
        print "proxy: " + str(current_proxy)
        start_time = datetime.datetime.now()
        createTwitterAccount(this_account_num)
        duration = datetime.datetime.now() - start_time
        print("time elapsed: " + str(duration.total_seconds()))
        GLOBAL['script_sleep'] = 10
    except Exception as e:
        print("+EE+: " + e.message)
        proxy_stats = getProxyStats(current_proxy)
        proxy_stats["failures"] += 1
        driver = CLOG["current_driver"]
        url = driver.current_url
        saveSpecialError(url)
        print "ERROR_URL: " + url
        GLOBAL['script_sleep'] = min(GLOBAL['script_sleep']*2, 2000)
        raise e
    else:
        proxy_stats = getProxyStats(current_proxy)
        proxy_stats["successes"] += 1
        good_proxies_file_path = os.path.join(PROJECT_PATH, "good_proxies.txt")
        good_proxies_file = open(good_proxies_file_path, "a")
        good_proxies_file.write(current_proxy + "\n")
        good_proxies_file.close()
    finally:
        try:
            driver = CLOG["current_driver"]
            if driver: driver.quit()
        except Exception as e:
            pass

def proxyGo(url, driver):
    to_return = driver.get(url)
    #sleep(10)
    return to_return

# create a twitter account using selenium
def createTwitterAccount(this_account_num):

    # set variables for registering
    twitter_account_username = random.choice(string.ascii_lowercase) \
                               + random.choice(string.ascii_lowercase) \
                               + TWITTER_ACCOUNT_USERNAME \
                               + random.choice(string.ascii_lowercase)
    twitter_email = twitter_account_username + str(this_account_num) + TWITTER_ACCOUNT_EMAIL_END
    twitter_app_name = TWITTER_APP_NAME + "  " + str(this_account_num) + random.choice(string.ascii_uppercase)
    twitter_username = twitter_account_username + str(this_account_num)
    debugger_log = CLOG

    current_proxy = CLOG["current_proxy"]
    proxy_stats = getProxyStats(current_proxy)
    driver = getWebDriver(proxy_string=current_proxy) # if current_proxy="" then there will be no proxy
    driver.delete_all_cookies()
    #script_sleep = GLOBAL.get("script_sleep")
    #if not script_sleep:
    #    script_sleep = GLOBAL['script_sleep'] = 10
    #print "SLEEPING_FOR: " + str(script_sleep)
    #saveSleep(script_sleep)
    #sleep(script_sleep)

    # check for auth
    #driver.set_page_load_timeout(10)
    #try:
    #    proxyGo("http://www.google.com", driver)
    #except Exception as e:
    #    try:
    #        alert = driver.switch_to_alert()
    #        if alert:
    #            ninja_username = "ninja38182"
    #            ninja_password = "ZjDrYPh472M5"
    #            alert.send_keys(ninja_username + "\t" + ninja_password + "\n")
    #    except:
    #        pass

    driver.set_page_load_timeout(120)
    # try to create a new twitter account with a proxied web driver
    try:
        proxyGo("http://twitter.com/signup", driver)
        sleep(10)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".prompt.password input")))
    except Exception as e:
        print "+XX+: BROKEN PROXY"
        proxy_stats["broken"] += 1
        CLOG["current_proxy"] = getRandomProxy()
        raise e

    sleep(10)
    name_field = driver.find_elements(By.CSS_SELECTOR, ".prompt.name input")[0]
    name_field.send_keys(TWITTER_ACCOUNT_NAME)
    email_field = driver.find_elements(By.CSS_SELECTOR, ".prompt.email input")[0]
    email_field.send_keys(twitter_email)
    password_field = driver.find_elements(By.CSS_SELECTOR, ".prompt.password input")[0]
    password_field.send_keys(TWITTER_ACCOUNT_PASSWORD)
    username_field = driver.find_elements(By.CSS_SELECTOR, ".prompt.username input")[0]
    username_field.send_keys(twitter_username)
    sleep(2)
    signup_button = driver.find_elements(By.CSS_SELECTOR, ".submit.button.promotional")[0]
    signup_button.click()
    sleep(10)
    # check for captcha
    captcha = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_image img")
    if len(captcha):
        captcha_image_tag = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_image img")[0]
        captcha_href = captcha_image_tag.get_attribute("src")
        captcha_local = 'tmp/captcha.jpg'
        urllib.urlretrieve(captcha_href, captcha_local)
        captcha_text = solveCaptcha(captcha_local)
        captcha_text_field = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_response_field")[0]
        captcha_text_field.send_keys(captcha_text)
        # click create account button again
        signup_button = driver.find_elements(By.CSS_SELECTOR, ".submit.button.promotional")[0]
        signup_button.click()
        sleep(10)
    # if we fucked up captcha
    captcha = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_image img")
    if len(captcha):
        captcha_image_tag = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_image img")[0]
        captcha_href = captcha_image_tag.get_attribute("src")
        captcha_local = 'tmp/captcha.jpg'
        urllib.urlretrieve(captcha_href, captcha_local)
        captcha_text = solveCaptcha(captcha_local)
        captcha_text_field = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_response_field")[0]
        captcha_text_field.send_keys(captcha_text)
        # click create account button again
        signup_button = driver.find_elements(By.CSS_SELECTOR, ".submit.button.promotional")[0]
        signup_button.click()
        sleep(10)

    # check if we were blacklisted
    error_page = driver.find_elements(By.CSS_SELECTOR, ".error-page h1")
    if len(error_page):
        print "+BB+: BLACKLISTED"
        proxy_stats["blacklisted"] = time.time()
        raise CreateTwitterAccountException("BLACKLISTED IP X_X")

    # confirm email
    sleep(2)
    mailinator_url = "http://" + twitter_username + ".mailinator.com"
    proxyGo(mailinator_url, driver)
    sleep(1)

    proxyGo(mailinator_url, driver)
    sleep(5)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.subject")))
    email_divs=driver.find_elements(By.CSS_SELECTOR, "div.subject")
    confirmation_email_button = None
    for x in email_divs:
        if "Confirm" in x.text:
            confirmation_email_button = x
    if not confirmation_email_button:
        print "+WW+: Didn't find confirmation email button first time"
        proxyGo(mailinator_url, driver)
        sleep(2)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.subject")))
        email_divs=driver.find_elements(By.CSS_SELECTOR, "div.subject")
        for x in email_divs:
            if "Confirm" in x.text:
                confirmation_email_button = x
        if not confirmation_email_button:
            raise CreateTwitterAccountException("Never found mailinator email link!")

    confirmation_email_button.click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.mailview")))
    email_links = driver.find_elements(By.CSS_SELECTOR, "div.mailview a")
    confirm_url = ""
    for x in email_links:
        href = x.get_attribute("href")
        if "confirm_email" in href:
            confirm_url = href
            break

    proxyGo(confirm_url, driver)
    # login

    # if account suspended, fill in another captcha
    account_suspended = driver.find_elements(By.CSS_SELECTOR, "#account-suspended")
    if len(account_suspended):
        proxyGo("http://twitter.com/account/suspended_help/", driver)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#recaptcha_image")))
        captcha_image_tag = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_image img")[0]
        captcha_href = captcha_image_tag.get_attribute("src")
        captcha_local = 'tmp/captcha.jpg'
        urllib.urlretrieve(captcha_href, captcha_local)
        captcha_text = solveCaptcha(captcha_local)
        captcha_text_field = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_response_field")[0]
        captcha_text_field.send_keys(captcha_text)
        # click confirm account button again
        confirm_button = driver.find_elements(By.CSS_SELECTOR, "input.btn.btn-m.btn-blue")[0]
        confirm_button.click()
        # login to twitter dev

    proxyGo("https://dev.twitter.com/user/login", driver)
    sleep(1)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#edit-name")))
    username_field = driver.find_elements(By.CSS_SELECTOR, "input#edit-name")[0]
    username_field.send_keys(twitter_username)
    password_field = driver.find_elements(By.CSS_SELECTOR, "input#edit-pass")[0]
    password_field.send_keys(TWITTER_ACCOUNT_PASSWORD)
    login_button = driver.find_elements(By.CSS_SELECTOR, "input#edit-submit")[0]
    login_button.click()
    sleep(5)
    # create a new app
    proxyGo("https://dev.twitter.com/apps/new", driver)
    sleep(2)
    proxyGo("https://dev.twitter.com/apps/new", driver)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#edit-tos-agreement")))
    sleep(5)
    name_field = driver.find_elements(By.CSS_SELECTOR, "input#edit-name")[0]
    name_field.send_keys(twitter_app_name)
    description_field = driver.find_elements(By.CSS_SELECTOR, "input#edit-description")[0]
    description_field.send_keys(TWITTER_APP_DESCRIPTION)
    website_field = driver.find_elements(By.CSS_SELECTOR, "input#edit-url")[0]
    website_field.send_keys(TWITTER_APP_WEBSITE)
    agree_checkbox = driver.find_elements(By.CSS_SELECTOR, "input#edit-tos-agreement")[0]
    agree_checkbox.click()
    captcha = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_image")
    if len(captcha):
        captcha_image_tag = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_image img")[0]
        captcha_href = captcha_image_tag.get_attribute("src")
        captcha_local = 'tmp/captcha.jpg'
        urllib.urlretrieve(captcha_href, captcha_local)
        captcha_text = solveCaptcha(captcha_local)
        captcha_text_field = driver.find_elements(By.CSS_SELECTOR, "#recaptcha_response_field")[0]
        captcha_text_field.send_keys(captcha_text)
    create_button = driver.find_elements(By.CSS_SELECTOR, "input#edit-submit")[0]
    create_button.click()
    # create access token
    sleep(2)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#edit-submit-owner-token")))
    create_token_button = driver.find_elements(By.CSS_SELECTOR, "input#edit-submit-owner-token")[0]
    create_token_button.click()
    sleep(10)
    proxyGo(driver.current_url, driver)
    sleep(2)
    create_token_button_again = driver.find_elements(By.CSS_SELECTOR, "input#edit-submit-owner-token")
    if len(create_token_button_again):
        create_token_button = create_token_button_again[0]
        create_token_button.click()
        sleep(15)
        proxyGo(driver.current_url, driver)
        sleep(5)
    twitter_credentials = {}
    consumer_key_tag = driver.find_elements(By.XPATH, "//table//tr//td[contains(text(),'Consumer key')]/following-sibling::td//tt")[0]
    twitter_credentials['consumer_key'] = consumer_key = consumer_key_tag.get_attribute("innerHTML")
    consumer_secret_tag = driver.find_elements(By.XPATH, "//table//tr//td[contains(text(),'Consumer secret')]/following-sibling::td//tt")[0]
    twitter_credentials['consumer_secret'] = consumer_secret = consumer_secret_tag.get_attribute("innerHTML")
    access_token_tag = driver.find_elements(By.XPATH, "//table//tr//td[contains(text(),'Access token')]/following-sibling::td")[1]
    twitter_credentials['my_key'] = my_key = access_token_tag.get_attribute("innerHTML")
    access_token_secret = driver.find_elements(By.XPATH, "//table//tr//td[contains(text(),'Access token secret')]/following-sibling::td")[0]
    twitter_credentials['my_secret'] = my_secret = access_token_secret.get_attribute("innerHTML")
    for k,v in twitter_credentials.items():
        print str(k) + ": " + str(v)
    if not (consumer_key and consumer_secret and my_key and my_secret):
        raise CreateTwitterAccountException(twitter_username)
    # else write the credentials to twitter_accounts file
    else:
        credentials_file_path = os.path.join(PROJECT_PATH, 'twitter_credentials.json')
        read_credentials_file = open(credentials_file_path, 'r')
        all_twitter_accounts = simplejson.loads(read_credentials_file.read())
        all_twitter_accounts.append(twitter_credentials)
        all_twitter_accounts_json = simplejson.dumps(all_twitter_accounts)
        read_credentials_file.close()
        write_credentials_file = open(credentials_file_path, 'w+')
        write_credentials_file.write(all_twitter_accounts_json)
        write_credentials_file.close()
        refreshTwitterAccounts()

# exceptions
class CreateTwitterAccountException(Exception):
    pass

def createManyTwitterAccounts():
    items = range(0,1000)
    item_fun = functools.partial(createTwitterAccountWrapper)
    monitor_script.runScript("create_twitter_accounts", items=items, item_fun=item_fun, resolution=5)

# main script
if __name__=="__main__":
    # candidate voter file from old db
    createManyTwitterAccounts()
