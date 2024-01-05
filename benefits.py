import pandas as pd
import os
import math
import hashlib
import json
import shutil
from dotenv import load_dotenv

load_dotenv()
FILENAME_CATEGORIES = os.environ.get("BENEFITS_FILENAME_CATEGORIES")
FILENAME_QUESTIONS = os.environ.get("BENEFITS_FILENAME_QUESTIONS")
FILENAME_CONTENT = os.environ.get("BENEFITS_FILENAME_CONTENT")
BUCKET = os.environ.get("BENEFITS_BUCKET")

questions = pd.read_csv(FILENAME_QUESTIONS)
def getContentForQuestion(question, options):
    row = questions.loc[questions['QuestionID'] == question]
    answers = []
    for option in options:
        answers.append( str(row[option].values[0]) )
    return f'Question: {row["QuestionText_en"].values[0]}\nAnswer: {", ".join(answers)}'

categories = pd.read_csv(FILENAME_CATEGORIES)
def getCategoryForCategory(category):
    row = categories.loc[categories['CategoryId'] == category]
    return row['CategoryName_en'].values[0]

content = pd.read_csv(FILENAME_CONTENT)


rows = []
for index, row in content.iterrows():
    benefitId = row['BenefitID']

    if not isinstance(benefitId, str) and math.isnan(benefitId):
        continue

    try:
        showifs = row['ShowIf'].replace(": ", ":").replace(" AND ", "&").replace(" ", "&")
        showifs = showifs.split("&")
        qas = []
        for showif in showifs:
            showif = showif.strip()
            parts = showif.split(":")

            if parts[1][0] == "O":
                options = parts[1].split(",")
                qa = getContentForQuestion(parts[0], options)
                qas.append(qa)
            elif parts[0] == "age" and parts[1][0] == "g":
                qas.append(f'Your age is greater than: {parts[2]}')
                age = parts[2]
            else:
                print(parts)
        qas = "\n".join(qas)
    except:
        pass

    row = {
        "benefitId": benefitId,
        "category": row['CategoryId'],
        "categoryName": getCategoryForCategory(row['CategoryId']),
        "title": row['Title_en'],
        "description": row['Content_en'],
        "link": row['Link_en'],
        "match": qas
    }
    rows.append(row)

try:
    os.makedirs(f'cache/benefits')
except:
    pass

try:
    os.makedirs(f'cache/benefits-txt')
except:
    pass

print(f"Writing {len(rows)} benefits to cache/benefits")

lines = []
for row in rows:
    key = hashlib.md5((str(row) ).encode('utf-8')).hexdigest()
    with open(f'cache/benefits/{key}.md', 'w') as f:
        f.write(f"Title: {row['title']}\n")
        f.write(f"---\n")
        f.write(f"Category: {row['categoryName']}\n")
        f.write(f"---\n")
        f.write(f"Match: {row['match']}\n")
        f.write(f"---\n")
        f.write(f"Link: {row['link']}\n")
        f.write(f"---\n")
        f.write(f"Description: {row['description']}\n")
    shutil.copyfile(f'cache/benefits/{key}.md', f'cache/benefits-txt/{key}.txt')

    jsonData = {
        "title": row['title'], 
        "description": row['description'],
        "url": row['link'],
        "category": row['categoryName'],
        "match": row['match']
    }

    line = {
        "id": f"foc-{key}",
        "jsonData": json.dumps(jsonData),
        "content": {
            "mimeType": "text/plain",
            "uri": f"gs://{BUCKET}/{key}.md",
        }
    }
    lines.append(line)

with open(f'cache/benefits/metadata.jsonl', 'w') as f:
    for line in lines:
        f.write(json.dumps(line) + '\n')






