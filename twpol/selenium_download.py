from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By

from time import sleep
import pdb

def seleniumLogIn(url, driver=None):
    if not driver:
        driver = webdriver.Chrome()
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".page-canvas .submit.btn.primary-btn")))
    driver.execute_script('$(".js-username-field").val("tresearch100");')
    driver.execute_script('$(".js-password-field").val("Lalala88");')
    driver.execute_script('$(".primary-btn").click();')


def seleniumDownloadFollowers(url, driver=None):
    if not driver:
        driver = webdriver.Chrome()
    driver.get(url)
    seleniumLogIn(url=url, driver=driver)
    driver.get(url)
    old_num_follower_tags = 0
    follower_tags = driver.find_elements_by_class_name("js-action-profile-avatar")
    num_follower_tags = len(follower_tags)
    #pdb.set_trace()
    while num_follower_tags > old_num_follower_tags:
        old_num_follower_tags = num_follower_tags
        driver.execute_script('window.scroll(0,document.height);')
        sleep(2)
        follower_tags = driver.find_elements_by_class_name("js-action-profile-avatar")
        num_follower_tags = len(follower_tags)
        print num_follower_tags
    follower_ids = set([])
    for x in follower_tags:
        follower_ids.add(x.get_attribute("data-user-id"))
    driver.quit()
    return follower_ids

def seleniumDownload():
    url = 'https://twitter.com/kanyewest/followers'
    seleniumDownloadFollowers(url)

