# -*- coding: UTF-8 -*-
"""
@FileName: download.py

@Author：zhuxinhao00@gmail.com

@Create date: 2020/3/31

@description: A script to download file automatically from teaching.applysquare.com
"""

import json
import logging
import os
import re
import time
from contextlib import closing

import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Load config from config.json
with open('config.json', 'r') as f:
    config = json.loads(f.read())

user_name = config.get('username')
user_passwd = config.get('password')
headless_mode = config.get('headless_mode')
download_all_ext = config.get('download_all_ext')
download_all_courses = config.get('download_all_courses')
ext_list = config.get('ext_list')
ext_expel_list = config.get('ext_expel_list')
cid_list = config.get('cid_list')

# Some metadata
login_url = r"https://teaching.applysquare.com/Home/User/login"
class_url_fmt = r"https://teaching.applysquare.com/S/Course/index/cid/{}#S-Course-info"
attachment_url_fmt = r'https://teaching.applysquare.com/Api/CourseAttachment/ajaxGetList/token/{}?p={}&status=1&plan_id=-1&all=0&pub_stat=1&uid={}&cid={}'
course_info_url_fmt = r'https://teaching.applysquare.com/Api/Public/getIndexCourseList/token/{}?type=1&usertype=1&uid={}'
token_pattern = r'(https://teaching\.applysquare\.com/Api/Public/getIndexCourseList/token/.*?)"'

# Start the webdriver
caps = DesiredCapabilities.CHROME
caps['loggingPrefs'] = {'performance': 'ALL'}
opt = webdriver.ChromeOptions()
opt.add_experimental_option('w3c', False)
opt.add_argument('log-level=3')
if headless_mode:
    opt.add_argument("--headless")
driver = webdriver.Chrome(options=opt, desired_capabilities=caps)

# Login to Pedagogy Square
driver.get(login_url)
time.sleep(1)

driver.find_element_by_xpath(r"/html/body/div[2]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/input").send_keys(user_name) # Send username
driver.find_element_by_xpath(r'//*[@id="id_login_password"]').send_keys(user_passwd) # Send password
driver.find_element_by_xpath(r'//*[@id="id_login_button"]').click() # Submit
print("Login Successfully!")

# Dealing with student-teacher selection
try:
    driver.find_element_by_xpath(r'/html/body/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/div[1]/i').click() # Choose student
    driver.find_element_by_xpath(r'/html/body/div[2]/div/div[2]/div/div/div[1]/div[4]/a').click() # Submit
except Exception:
    pass

# Get token for authorization
token = None
while not token:
    for entry in driver.get_log('performance'):
        match_obj = re.search(token_pattern, entry.get('message'))
        if match_obj:
            temp_url = match_obj.group(1)
            token = re.search(r'token/(.*?)\?', temp_url).group(1)
            uid = re.search(r'uid=(.*?)', temp_url).group(1)
            break

cid2name_dict = dict()
course_info_url = course_info_url_fmt.format(token, uid)
driver.get(course_info_url)
raw_info = re.search(r'\{.*\}', driver.page_source).group(0)
info = json.loads(raw_info).get('message')
for entry in info:
    cid2name_dict[entry.get('cid')] = entry.get('name')

if download_all_courses:
    cid_list = cid2name_dict.keys()

for cid in cid_list:
    course_name = cid2name_dict[cid]

    # Create dir for this course
    try:
        os.chdir("./{}".format(course_name))
    except FileNotFoundError:
        os.mkdir("{}".format(course_name))
        os.chdir("./{}".format(course_name))

    # Get attachment metadata
    attachment_list = list()
    attachment_info_url = attachment_url_fmt.format(token, 1, uid, cid)
    driver.get(attachment_info_url)
    raw_info = re.search(r'\{.*\}', driver.page_source).group(0)
    info = json.loads(raw_info).get('message')
    total_pages = info.get('total_pages')
    print("\nDownloading files of course {}".format(course_name))
    print("Get {:d} files".format(info.get('total')))

    # Add attachment path to attachment_list
    for current_page in range(1, total_pages+1):
        current_url = attachment_url_fmt.format(token, current_page, uid, cid)
        driver.get(current_url)
        raw_info  = re.search(r'\{.*\}', driver.page_source).group(0)
        info = json.loads(raw_info).get('message')
        attachment_list.extend(info.get('rows'))

    # Download attachments
    for entry in attachment_list:
        if (entry.get('ext') not in ext_expel_list) and (download_all_ext or entry.get('ext') in ext_list):
            filename = entry.get('filename')
            filesize = entry.get('size')
            if filename in os.listdir():
                print("File \"{}\" already exists!".format(filename))
                continue
            else:
                print("Downloading {}, filesize = {}".format(filename, filesize))

            with closing(requests.get(entry.get('path').replace('amp;', ''), stream=True)) as res:
                content_size = int(res.headers['content-length'])
                chunk_size = min(content_size, 10240)
                with open(filename, "wb") as f:
                    chunk_count = 0
                    start_time = time.time()
                    total = content_size / 1024 / 1024
                    for data in res.iter_content(chunk_size=chunk_size):
                        chunk_count += 1
                        processed = len(data) * chunk_count / 1024 / 1024
                        current_time = time.time()
                        if chunk_count < 5:
                            print(r"    Total: {:.2f} MB  Processed: {:.2f} MB ({:.2f}%)".format(total, processed, processed/total*100), end = '\r')
                        else:
                            ETA = (current_time-start_time)/processed*(total-processed)
                            print(r"    Total: {:.2f} MB  Processed: {:.2f} MB ({:.2f}%), ETA {:.2f}s".format(total, processed, processed/total*100, ETA), end = '\r')
                        f.write(data)

    os.chdir(r'../') # Switch directory

print("Done!")
