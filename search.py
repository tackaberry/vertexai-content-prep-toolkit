import requests
import os
import json
import hashlib
from bs4 import BeautifulSoup
import markdownify 
from dotenv import load_dotenv

load_dotenv()
SEARCH_SESSION_KEY = os.environ.get("SEARCH_SESSION_KEY")
SEARCH_BUCKET = os.environ.get("SEARCH_BUCKET")

def get_search_page(term, page):

    print(f'Getting page {page} for {term}')

    URL = os.environ.get("SEARCH_URL_1")
    # requests with post method
    payload = {
        "query":term,
        "filters":{"all":[
            {"any":[{"lang":"en"},{"lang":"en-US"},{"lang":"en en"},{"lang":"en-ca"},{"lang":""}]},
            {"none":[{"url_host":os.environ.get("SEARCH_URL_3")}]},
            {"none":[{"archived":"true"}]}]
        },
        "result_fields":{
            "lang":{"raw":{},"snippet":{"size":100,"fallback":True}},
            "meta_description":{"raw":{},"snippet":{"size":100,"fallback":True}},
            "title":{"raw":{},"snippet":{"size":100,"fallback":True}},
            "url":{"raw":{},"snippet":{"size":100,"fallback":True}},
            "drupal_metadata":{"raw":{},"snippet":{"size":100,"fallback":True}},
            "id":{"raw":{},"snippet":{"size":100,"fallback":True}}},
        "page":{"size":100,"current":page}}
    headers = {
        "method": "POST",
        "content-type": "application/json",
        "Origin": f'{os.environ.get("SEARCH_URL_2")}',
        "Referer": f'{os.environ.get("SEARCH_URL_2")}/search',
        "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Sec-Ch-Ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "Authorization": f"Bearer {SEARCH_SESSION_KEY}"

    }
    key = hashlib.md5((URL + str(headers) + str(payload) ).encode('utf-8')).hexdigest()

    # if cache exists, use cache
    try:
        with open(f'cache/search/{key}.json', 'r') as f:
            json_data = json.load(f)
    except:
        page = requests.post(URL, data=str(payload), headers=headers)
        json_data = page.json()

        with open(f'cache/search/{key}.json', 'w') as f:
            json.dump(json_data, f)

    return json_data

def prepare_directiories():
    # if directory does not exist, create directory
    try:
        os.makedirs(f'cache/search')
    except:
        pass

    try:
        os.makedirs(f'cache/content')
    except:
        pass

    try:
        os.makedirs(f'cache/html')
    except:
        pass

    try:
        os.makedirs(f'cache/markdown')
    except:
        pass

    try:
        os.makedirs(f'cache/errors')
    except:
        pass


def get_search_pages(term):

    print(f"Getting search pages for {term}")

    page_number = 1
    last_page = None

    while last_page is None or page_number <= last_page:
        results = get_search_page(term, page_number)
        last_page = results["meta"]["page"]["total_pages"]
        print(f'Got: {results["meta"]["page"]}')
        page_number += 1


def get_rows_from_searches():

    rows = []

    # iteratre through all search pages in search directory
    for filename in os.listdir(f'cache/search'):

        # open the file
        with open(f'cache/search/{filename}', 'r') as f:
            results = json.load(f)

        for result in results["results"]:
            try:
                tags = {}

                if 'drupal_metadata' in result:
                    meta = json.loads(result['drupal_metadata']['raw'])
                    if 'topicTag' in meta:
                        topicTags=meta['topicTag'].split("|")
                        tags['topicTag'] = topicTags
                    if 'ministryTag' in meta:
                        tags['ministryTag'] = meta['ministryTag']
                    if 'contentTypeTag' in meta:
                        tags['contentTypeTag'] = meta['contentTypeTag']
                row = {
                    'title': result['title']['raw'],
                    'url': result['url']['raw'],
                    'description': result['meta_description']['raw'] if 'meta_description' in result else None,
                    'language': result['lang']['raw'],
                    'id': result['id']['raw'],
                    'tags': tags
                }
                rows.append(row)
            except Exception as e:
                print(e)
                print(result)
                continue
    
    return rows

prepare_directiories()
get_search_pages(os.environ.get("SEARCH_TERM_1"))
get_search_pages(os.environ.get("SEARCH_TERM_2"))

rows = get_rows_from_searches()


lines = []
for row in rows:

    key = hashlib.md5(row['url'].encode('utf-8')).hexdigest()

    # get html from url
    try:
        with open(f'cache/html/{key}.html', 'r') as f:
            html = f.read()

    except:
        html = requests.get(row['url']).text
        with open(f'cache/html/{key}.html', 'w') as f:
            f.write(html)

    # get content from html
    try:
        with open(f'cache/content/{key}.html', 'r') as f:
            content = f.read()
    except:

        try: 
            page = BeautifulSoup(html, 'html.parser')
            content = page.find(id="main-content")
            if content is None:
                content = page.find("main")
            content = content.prettify()

            with open(f'cache/content/{key}.html', 'w') as f:
                f.write(content)
        except Exception as e:
            print(e)
            print(key)
            print(row['url'])
            # copy the file to the error directory
            with open(f'cache/errors/{key}.html', 'w') as f:
                f.write(html)
            continue

    # convert content to markdown
    try:
        with open(f'cache/markdown/{key}.md', 'r') as f:
            markdown = f.read()
    except:
        try:
            markdown  = markdownify.markdownify(content, heading_style="ATX")
            with open(f'cache/markdown/{key}.md', 'w') as f:
                f.write(markdown)
        except Exception as e:
            print(e)
            print(key)
            print(row['url'])
            # copy the file to the error directory
            with open(f'cache/errors/{key}.html', 'w') as f:
                f.write(content)
            continue

    jsonData = {
            "title": row['title'],
            "description": row['description'],
            "url": row['url'],
            "language": row['language'],
            "tags": row['tags'],
        }

    line = {
        "id": f"foc-{key}",
        "jsonData": json.dumps(jsonData),
        "content": {
            "mimeType": "text/plain",
            "uri": f"gs://{SEARCH_BUCKET}/{key}.md",
        }
    }
    lines.append(line)

with open(f'cache/markdown/metadata.jsonl', 'w') as f:
    for line in lines:
        f.write(json.dumps(line) + '\n')



