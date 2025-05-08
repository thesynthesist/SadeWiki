import requests

GITHUB_API = "https://api.github.com"
headers = {"X-GitHub-Api-Version" : "2022-11-28"}

def get(path):
    r = requests.get(GITHUB_API + path, headers=headers)
    return r

def check_repo(repo):
    r = get("/repos/" + repo)
    return r

token = input("Please input your token for access: ")    
headers["Authorization"] = "Bearer " + token
check_auth = get("/user")
if not check_auth.ok:
    exit("Error on authenticating, please check token")
else :
    username = check_auth.json()["login"]
    print(f"Logged in as {username}")
    
while True:
    repo = input("Please specify the repo you would like to work on: ")
    res = check_repo(repo)
    if not res.ok :
        print(res.status_code)
    else :
        print(res.json()["permissions"])