import json
import os
import time
import shutil
from glob import glob
import requests

GITHUB_API = "https://api.github.com"
headers = {"X-GitHub-Api-Version" : "2022-11-28"}
output_directory = "output"
css_file = "styles.css"

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

shutil.copy(css_file, output_directory + "/" + css_file)

def check_status(response):
    response_headers = response.headers
    if response_headers["x-ratelimit-remaining"] == '0':
        print("Rate limit hit, waiting to avoid ban...")
        ratelimit_reset = response_headers["x-ratelimit-reset"]
        current_time = time.time()
        wait_time = int(ratelimit_reset) - int(current_time)
        print(f"Rate limit hit, will resume in {wait_time} seconds...")
        time.sleep(wait_time)
        # TODO: This works, but the lack of output makes it a bit annoying. Could do with a loop to output current wait time
    elif not response.ok:
        exit(f"Request failed with status code: {response.status_code}")

def get_files(src_directory):
    files = glob(src_directory + "/*.md")
    return files

def get(path):
    r = requests.get(GITHUB_API + path, headers=headers)
    check_status(r)
    return r

def post(path, data):
    r = requests.post(GITHUB_API + path, headers=headers, data=data)
    check_status(r)
    return r

def get_html(markdown):
    content_json = {"text": markdown}
    r = post("/markdown", data=json.dumps(content_json))
    return r.text

def check_repo(repo):
    r = get("/repos/" + repo)
    return r

def authenticate():
    token = input("Please input your token for access: ")
    headers["Authorization"] = "Bearer " + token
    check_auth = get("/user")
    if not check_auth.ok:
        exit("Error on authenticating, please check token")
    else :
        username = check_auth.json()["login"]
        print(f"Logged in as {username}")

src_directory = 'src'

if __name__ == "__main__":
    files = get_files(src_directory)
    for each_file in files:
        handler = open(each_file, "r")
        content = handler.read()
        html = get_html(content)
        output_file = each_file.replace(".md", ".html")
        output_file = output_directory + output_file[len(src_directory):]
        with open(output_file, "w") as f:
            f.write(f'<link rel="stylesheet" href="{css_file}">\n')
            f.write(html)