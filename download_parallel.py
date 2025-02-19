# -*- coding: UTF-8 -*-
"""
@FileName: download_parallel.py

@Author: zhuxinhao00@gmail.com
@Author: twinklerchn@gmail.com

@Create date: 2025/2/19

@Modified date: 2025/2/19

@description: A script to download file automatically from teaching.applysquare.com concurrently
"""

import hashlib
import json
import os
import pathlib
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Get Hex-md5 encoded password
def hex_md5_stringify(raw_str: str):
    md5_encoder = hashlib.md5()
    md5_encoder.update(str(raw_str).encode("utf-8"))
    return md5_encoder.hexdigest()


# Function dealing with illegal characters of windows filename
def filename_filter(name: str):
    illegal_list = list('/\:*?”"<>|')
    for char in illegal_list:
        name = name.replace(char, " ")
    return name


def construct_attchment_list(sess, token, pid, uid, cid, parent_dir):
    attachment_list = list()
    attachment_info_url = attachment_url_fmt.format(token, pid, 1, uid, cid)
    r = sess.get(attachment_info_url, verify=False)
    info = r.json()["message"]
    file_num = info.get("count")

    current_page = 1
    # Add attachment path to attachment_list
    while len(attachment_list) < file_num:
        current_url = attachment_url_fmt.format(token, pid, current_page, uid, cid)
        r = sess.get(current_url, verify=False)
        info = r.json()["message"]
        attachment_list.extend(info.get("list"))
        current_page += 1
    for entry in attachment_list:
        entry["parent_dir"] = parent_dir
    return attachment_list


# Load config from config.json
with open("config.json", "r", encoding="utf-8") as f:
    config = json.loads(f.read())
    user_name = config.get("username")
    user_passwd = config.get("password")
    ext_expel_list = config.get("ext_expel_list")
    cid_include_list = list(map(str, config.get("cid_include_list", [])))
    cid_expel_list = list(map(str, config.get("cid_expel_list", [])))
    save_path = config.get("save_path", "")
    keep_dirs = config.get("keep_dirs", False)

if save_path:
    try:
        os.chdir(save_path)
    except Exception as e:
        print(
            'Changing save_path failed for reason "{}", using default path instead.'.format(
                e
            )
        )
        time.sleep(1)

print("Files will be saved to ", os.getcwd())

# Some metadata
login_url = r"https://teaching.applysquare.com/Api/User/ajaxLogin"
attachment_url_fmt = r"https://teaching.applysquare.com/Api/CourseAttachment/getList/token/{}?parent_id={}&page={}&plan_id=-1&uid={}&cid={}"
course_info_url_fmt = r"https://teaching.applysquare.com/Api/Public/getIndexCourseList/token/{}?type=1&usertype=1&uid={}"
attachment_detail_url_fmt = r"https://teaching.applysquare.com/Api/CourseAttachment/ajaxGetInfo/token/{}?id={}&uid={}&cid={}"

# Init Requests session
sess = requests.Session()

# Login in
print("Trying to log in, please wait ...")
login_request = sess.post(
    login_url,
    data={"email": user_name, "password": hex_md5_stringify(user_passwd)},
    verify=False,
)

login_response = login_request.json()
login_info = login_response["message"]

try:
    token = login_info["token"]
except TypeError:
    print("Login Failed, please check your username & password")
    print("Login info received: {}".format(login_info))
    exit()

uid = login_info["uid"]
print("Login successfully!")

cid2name_dict = dict()
course_info_url = course_info_url_fmt.format(token, uid)
r = sess.get(course_info_url, verify=False)
info = r.json()["message"]
for entry in info:
    cid2name_dict[entry.get("cid")] = entry.get("name")

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


def download_cid(cid):
    cid = str(cid)  # Prevent bug caused by wrong type of cid

    if not check_cid(cid):
        return

    try:
        course_name = filename_filter(cid2name_dict[cid])
    except KeyError:
        print(
            "Can't find course name for cid {}, maybe it's a legacy course?".format(cid)
        )
        course_name = "CID_{}".format(cid)
    print("\nDownloading files of course {}".format(course_name))

    # Create dir for this course
    root = pathlib.Path(os.getcwd()) / course_name
    if not root.exists() or root.is_file():
        os.makedirs(root)

    # Construct attachment list, with some dirs in it
    course_attachment_list = construct_attchment_list(
        sess=sess, token=token, pid=0, uid=uid, cid=cid, parent_dir=pathlib.Path(".")
    )

    # Iteratively add files in dirs to global attachment list
    dir_counter = 0
    for entry in course_attachment_list:
        if entry.get("ext") == "dir":
            dir_counter += 1
            # Add dir content to attachment list
            dir_id = entry.get("id")
            dir_name = filename_filter(entry.get("title")) if keep_dirs else ""
            parent_dir = entry.get("parent_dir")
            if not (root / parent_dir / dir_name).exists():
                os.makedirs(root / parent_dir / dir_name)
            course_attachment_list.extend(
                construct_attchment_list(
                    sess=sess,
                    token=token,
                    pid=dir_id,
                    uid=uid,
                    cid=cid,
                    parent_dir=parent_dir / dir_name,
                )
            )

    print(
        "Get {:d} files with {:d} dirs".format(
            len(course_attachment_list) - dir_counter, dir_counter
        )
    )

    def download_entry(entry):
        ext = entry.get("ext")
        if (ext == "dir") or (ext in ext_expel_list):
            return

        if ext in entry.get("title"):
            filename = filename_filter(entry.get("title"))
        else:
            filename = filename_filter("{}.{}".format(entry.get("title"), ext))
        filepath = root / entry.get("parent_dir") / filename

        filesize = entry.get("size")

        # Get download url for un-downloadable files
        if entry.get("can_download") == "0":
            attachment_detail_url = attachment_detail_url_fmt.format(
                token, entry.get("id"), uid, cid
            )
            r = sess.get(attachment_detail_url, verify=False)
            info = r.json()["message"]
            entry["path"] = info.get("path")

        # Streaming, so we can iterate over the response
        response = requests.get(entry.get("path").replace("amp;", ""), stream=True)

        try:
            content_size = eval(response.headers["content-length"])
        except Exception:
            print(
                "Failed to get content length of file {}, please download it manually.".format(
                    filename
                )
            )
            return

        if filepath.exists() and filepath.is_file():
            # If file is up-to date, continue; else, delete and re-download
            if os.path.getsize(filepath) == content_size:
                print("File {:\u3000<20} is up-to-date".format(filename))
                return
            else:
                print("Updating File {}".format(filename))
                os.remove(filepath)

        chunk_size = min(content_size, 10240)

        with tqdm(total=content_size, unit="B", unit_scale=True, desc=f"Downloading {filename}") as progress_bar:
            with open(filepath, "wb") as file:
                for data in response.iter_content(chunk_size):
                    progress_bar.update(len(data))
                    file.write(data)

    # Download attachments
    with ThreadPoolExecutor(max_workers=8) as exe:
        exe.map(download_entry, course_attachment_list)


with ThreadPoolExecutor(max_workers=8) as exe:
    exe.map(download_cid, cid_list)

print("Done!")
