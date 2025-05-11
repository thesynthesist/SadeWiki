import json
from glob import glob
import requests

GITHUB_API = "https://api.github.com"
headers = {"X-GitHub-Api-Version" : "2022-11-28"}
output_directory = "./output"

def get_files(src_directory):
    files = glob(src_directory + "/*.md")
    return files

def get(path):
    r = requests.get(GITHUB_API + path, headers=headers)
    return r

def post(path, data):
    r = requests.post(GITHUB_API + path, headers=headers, data=data)
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

if __name__ == "__main__":
    files = get_files('src')
    for each_file in files:
        handler = open(each_file, "r")
        content = handler.read()
        html = get_html(content)