# -*- coding: UTF-8 -*-
"""
@FileName: download.py

@Author：zhuxinhao00@gmail.com

@Create date: 2020/03/31

@Modified date: 2021/09/14

@description: A script to download file automatically from teaching.applysquare.com
"""

import hashlib
import json
import logging
import os
import pathlib
import re
import time
from contextlib import closing

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Get Hex-md5 encoded password
def hex_md5_stringify(raw_str:str):
    md5_encoder = hashlib.md5()
    md5_encoder.update(str(raw_str).encode('utf-8'))
    return md5_encoder.hexdigest()

# Function dealing with illegal characters of windows filename
def filename_filter(name:str):
    illegal_list = list('/\:*?”"<>|')
    for char in illegal_list:
        name = name.replace(char, ' ')
    return name

def construct_attchment_list(sess, token, pid, uid, cid, parent_dir):
    attachment_list = list()
    attachment_info_url = attachment_url_fmt.format(token, pid, 1, uid, cid)
    r = sess.get(attachment_info_url, verify=False)
    info = r.json()['message']
    file_num = info.get('count')

    current_page = 1
    # Add attachment path to attachment_list
    while len(attachment_list) < file_num:
        current_url = attachment_url_fmt.format(token, pid, current_page, uid, cid)
        r = sess.get(current_url, verify=False)
        info = r.json()['message']
        attachment_list.extend(info.get('list'))
        current_page += 1
    for entry in attachment_list:
        entry["parent_dir"] = parent_dir
    return attachment_list

# Load config from config.json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.loads(f.read())
    user_name = config.get('username')
    user_passwd = config.get('password')
    ext_expel_list = config.get('ext_expel_list')
    cid_include_list = list(map(str, config.get('cid_include_list', [])))
    cid_expel_list = list(map(str, config.get('cid_expel_list', [])))
    save_path = config.get('save_path', "")
    keep_dirs = config.get('keep_dirs', False)

if save_path:
    try:
        os.chdir(save_path)
    except Exception as e:
        print('Changing save_path failed for reason \"{}\", using default path instead.'.format(e))
        time.sleep(1)

print("Files will be saved to ", os.getcwd())

# Some metadata
login_url = r'https://teaching.applysquare.com/Api/User/ajaxLogin'
attachment_url_fmt = r'https://teaching.applysquare.com/Api/CourseAttachment/getList/token/{}?parent_id={}&page={}&plan_id=-1&uid={}&cid={}'
course_info_url_fmt = r'https://teaching.applysquare.com/Api/Public/getIndexCourseList/token/{}?type=1&usertype=1&uid={}'
attachment_detail_url_fmt = r'https://teaching.applysquare.com/Api/CourseAttachment/ajaxGetInfo/token/{}?id={}&uid={}&cid={}'

# Init Requests session
sess = requests.Session()

# Login in
print("Trying to log in, please wait ...")
login_request = sess.post(login_url, data={"email" : user_name, "password" : hex_md5_stringify(user_passwd)}, verify=False)

login_response = login_request.json()
login_info = login_response['message']

try:
    token = login_info['token']
except TypeError:
    print("Login Failed, please check your username & password")
    print("Login info received: {}".format(login_info))
    exit()

uid = login_info['uid']
print("Login successfully!")

cid2name_dict = dict()
course_info_url = course_info_url_fmt.format(token, uid)
r = sess.get(course_info_url, verify=False)
info = r.json()["message"]
for entry in info:
    cid2name_dict[entry.get('cid')] = entry.get('name')

cid_list = cid2name_dict.keys()

def check_cid(cid):
    if len(cid_include_list) and cid not in cid_include_list:
        return False
    return cid not in cid_expel_list

print("\nReady to download the following courses:")
for cid, cname in cid2name_dict.items():
    if not check_cid(cid):
        continue
    print("Course: {:8s}, CID={:6}".format(cname, cid))

for cid in cid_list:
    cid = str(cid) # Prevent bug caused by wrong type of cid

    if not check_cid(cid):
        continue

    try:
        course_name = filename_filter(cid2name_dict[cid])
    except KeyError:
        print("Can't find course name for cid {}, maybe it's a legacy course?".format(cid))
        course_name = "CID_{}".format(cid)
    print("\nDownloading files of course {}".format(course_name))

    # Create dir for this course
    root= pathlib.Path(os.getcwd()) / course_name
    if not root.exists() or root.is_file():
        os.makedirs(root)

    # Construct attachment list, with some dirs in it
    course_attachment_list = construct_attchment_list(sess=sess, token=token, pid=0, uid=uid, cid=cid, parent_dir=pathlib.Path("."))

    # Iteratively add files in dirs to global attachment list
    dir_counter = 0
    for entry in course_attachment_list:
        if (entry.get('ext') == 'dir'):
            dir_counter += 1
            # Add dir content to attachment list
            dir_id = entry.get('id')
            dir_name = filename_filter(entry.get('title')) if keep_dirs else ''
            parent_dir = entry.get('parent_dir')
            if not (root/parent_dir/dir_name).exists():
                os.makedirs(root/parent_dir/dir_name)
            course_attachment_list.extend(construct_attchment_list(sess=sess, token=token, pid=dir_id, uid=uid, cid=cid, parent_dir=parent_dir/dir_name))

    print("Get {:d} files with {:d} dirs".format(len(course_attachment_list)-dir_counter, dir_counter))

    # Download attachments
    for entry in course_attachment_list:
        ext = entry.get('ext')
        if (ext == 'dir') or (ext in ext_expel_list):
            continue

        if (ext in entry.get('title')):
            filename = filename_filter(entry.get('title'))
        else:
            filename = filename_filter("{}.{}".format(entry.get('title'), ext))
        filepath = root/entry.get("parent_dir")/filename

        filesize = entry.get('size')

        # Get download url for un-downloadable files
        if (entry.get('can_download') == '0'):
            attachment_detail_url = attachment_detail_url_fmt.format(token, entry.get('id'), uid, cid)
            r = sess.get(attachment_detail_url, verify=False)
            info = r.json()['message']
            entry['path'] = info.get('path')

        with closing(requests.get(entry.get('path').replace('amp;', ''), stream=True)) as res:

            try:
                content_size = eval(res.headers['content-length'])
            except Exception:
                print("Failed to get content length of file {}, please download it manually.".format(filename))
                continue

            if filepath.exists() and filepath.is_file():
                # If file is up-to date, continue; else, delete and re-download
                if os.path.getsize(filepath) == content_size:
                    print("File {:\u3000<20} is up-to-date".format(filename))
                    continue
                else:
                    print("Updating File {}".format(filename))
                    os.remove(filepath)

            print("Downloading {:\u3000<20s}, filesize = {}".format(filename, filesize))
            chunk_size = min(content_size, 10240)
            with open(filepath, "wb") as f:
                chunk_count = 0
                start_time = time.time()
                # previous_time = time.time()
                # lag_counter = 0
                total = content_size / 1024 / 1024
                for data in res.iter_content(chunk_size=chunk_size):
                    chunk_count += 1
                    processed = len(data) * chunk_count / 1024 / 1024
                    current_time = time.time()
                    if chunk_count < 5:
                        print(r"    Total: {:.2f} MB  Processed: {:.2f} MB ({:.2f}%)".format(total, processed, processed/total*100), end = '\r')
                    else:
                        remaining = (current_time-start_time)/processed*(total-processed)
                        print(r"    Total: {:.2f} MB  Processed: {:.2f} MB ({:.2f}%), ETA {:.2f}s".format(total, processed, processed/total*100, remaining), end = '\r')
                    f.write(data)

                    # speed = chunk_size / 1.0 * (current_time - previous_time)
                    # if speed < speed_threshold:
                    #     lag_counter += 1
                    # else:
                    #     lag_counter = 0

                    # if lag_counter > 10:
                    #     print("Restart downloading of file {}".format(filename))
                    #     attachment_list.append(entry)
                    #     continue


print("Done!")
