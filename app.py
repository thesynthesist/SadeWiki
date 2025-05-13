import json
import os
import time
import shutil
from glob import glob
import requests
import http.server
import socketserver

GITHUB_API = "https://api.github.com"
headers = {"X-GitHub-Api-Version" : "2022-11-28"}
output_directory = "output"
css_file = "styles.css"

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

shutil.copy(css_file, output_directory + "/" + css_file)

def check_status(response):
    """
    When a response is passed to this, this function will ensure the request is checked for any potential issues.
    A rate limit header reaching 0 will cause the code to pause for the required period. And any non 200 status code will cause the code to exit
    :param response:
    :return None:
    """
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
    """
    Get markdown files from the source directory
    :param src_directory:
    :return List of filenames as strings:
    """
    files = glob(src_directory + "/*.md")
    return files

def get(path):
    """
    Makes a GET request to the given path using the API headers
    :param path:
    :return response object:
    """
    r = requests.get(GITHUB_API + path, headers=headers)
    check_status(r)
    return r

def post(path, data):
    """
    Makes a POST request to the given path using the API headers and data. JSON data must be formatted using json.dumps
    :param path:
    :param data:
    :return response object:
    """
    r = requests.post(GITHUB_API + path, headers=headers, data=data)
    check_status(r)
    return r

def get_html(markdown):
    """
    Makes a request to the Github API to change markdown into HTML
    :param markdown:
    :return HTML as string:
    """
    content_json = {"text": markdown}
    r = post("/markdown", data=json.dumps(content_json))
    return r.text

def authenticate():
    """
    Prompts the user for a token and exits if token is not correct
    :return:
    """
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
    print("Done!")
    PORT = 8000
    handler = http.server.SimpleHTTPRequestHandler
    os.chdir(output_directory)
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        # TODO: Make this server port and address dynamic
        print(f"Serving at http://{httpd.server_address[0]}:{httpd.server_address[1]}/")
        print("Press Ctrl+C to exit")
        try :
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Keyboard interrupt received, exiting...")
            httpd.server_close()
            exit(0)