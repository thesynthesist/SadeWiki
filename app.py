import json
import os
import time
import shutil
from glob import glob
import requests
import http.server
import socketserver
import classes

GITHUB_API = "https://api.github.com"
headers = {"X-GitHub-Api-Version" : "2022-11-28"}

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
        raise classes.GitHubApiError(f"{response.status_code} {response.reason} returned on {response.request.method} request {response.url} - View GitHub REST API docs for more guidance")

def get_files():
    """
    Get markdown files from the source directory
    :return List of filenames as strings:
    """
    files = glob("*.md")
    #files = glob("*/*.md") # TODO: Make recursive files work correctly, right now it fails on write
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

def authenticate(token):
    """
    Prompts the user for a token and exits if token is not correct
    :return user object:
    """
    headers["Authorization"] = "Bearer " + token
    check_auth = get("/user")
    if not check_auth.ok:
        raise classes.InvalidToken(f"Error on authenticating, please check token. Status code: {check_auth.status_code} returned")
    else :
        user_object = check_auth.json()
        return user_object

if __name__ == "__main__":
    css_file = "/styles.css"
    #token = os.environ["SADE_GH_TOKEN"]
    output_directory = os.environ["GITHUB_WORKSPACE"] + "docs"

    files = get_files()
    print(f"Found {len(files)} markdown files to process")
    #auth = authenticate(token)

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    shutil.copy(css_file, output_directory + "/" + css_file)

    index = []

    for each_file in files:
        handler = open(each_file, "r")
        content = handler.read()
        html = get_html(content)
        output_file = each_file.replace(".md", ".html")
        output_file = output_directory + "/" + output_file
        index.append(output_file)
        with open(output_file, "w") as f:
            f.write(f'<link rel="stylesheet" href="{css_file}">\n')
            f.write(html)

    with open(output_directory + "/index.html", "w") as index_file:
        index_file.write(f'<link rel="stylesheet" href="{css_file}">\n')
        index_file.write("<ul>\n")
        for link in index :
            index_file.write(f"<li><a href='/{link}'>{link}</a></li>\n")
        index_file.write("</ul>\n")

    print("Done!")
    PORT = 8000
    """
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        # TODO: Make this server port and address dynamic
        print(f"Serving at http://{httpd.server_address[0]}:{httpd.server_address[1]}/{output_directory}/")
        print("Press Ctrl+C to exit")
        try :
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Keyboard interrupt received, exiting...")
            httpd.server_close()
            exit(0)
    """