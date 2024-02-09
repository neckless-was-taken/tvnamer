from glob import glob
import json
import logging
import os
import sys

from openai import OpenAI
from thefuzz import fuzz

extensions = ['mkv','avi','mp4']

torrentSource = '/srv/maven/Torrents/Completed/'
destinationFolder = '/srv/maven/Media/Movies/'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/srv/maven/scripts/tvnamer/torrent-completed.log')
    ]
)

def chatgpt(prompt):
    for i in range(2):
        client = OpenAI(api_key="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")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="gpt-3.5-turbo",
        )
        modelReply = chat_completion.choices[0].message.content
        try:
            modelReply = json.loads(chat_completion.choices[0].message.content)
            logging.info(f'ChatGPT response: {modelReply}')
            modelReply = {k.lower(): v for k, v in modelReply.items()}
            if str(modelReply.get('name')) == None:
                modelReply['category'] = 'None'
            if str(modelReply.get('year')) == None:
                modelReply['category'] = 'None'
            if str(modelReply.get('category')) == None:
                modelReply['category'] = 'None'
            return modelReply
        except json.JSONDecodeError:
            if i == 1:
                logging.error('ChatGPT gave an invalid response two times in a row')
                logging.error(f'Last ChatGPT response: {chat_completion.choices[0].message.content}')
                raise json.JSONDecodeError('ChatGPT gave an invalid response two times in a row')
            else:
                continue

def TVMover(torrentPath):
    print(torrentPath)
    os.system(f'tvnamer --config=/srv/maven/scripts/tvnamer/config.json --move --recursive --batch "{torrentPath}"')
    # replace sys.exit() with an exit function that cleans left over files
    sys.exit()

def MovieMover(newName):
    try:
        os.rename(torrentPath, os.path.join(destinationFolder, newName))
        logging.debug(f'Torrent moved from: {torrentPath} to {os.path.join(destinationFolder, newName)}')
    except FileNotFoundError:
        logging.error(f'Folder {torrentPath} can not be found')
        raise FileExistsError(f'Folder {torrentPath} can not be found')
    except FileExistsError:
        logging.error(f'Folder {os.path.join(destinationFolder, newName)} already exists')
        raise FileExistsError(f'Folder {os.path.join(destinationFolder, newName)} already exists')
    # replace sys.exit() with an exit function that cleans left over files
    sys.exit()

def OtherMover():
    logging.debug('OtherMover not yet set up smiley face :)')
    # replace sys.exit() with an exit function that cleans left over files
    sys.exit()

# NEEDS REWRITE
if len(sys.argv) != 4:
    logging.debug(f'Unexpected amount of arguments were passed')
    torrentPath = max(glob(os.path.join(torrentSource, '*/')), key=os.path.getmtime)
    torrentName = torrentPath.replace(torrentSource, '')
    for file in os.listdir(torrentPath):
        if file.split('.')[-1] in extensions:
            if fuzz.partial_ratio(torrentName, file) > 90:
                pass
        else:
            logging.error('No suitable video files was found!')
            raise FileNotFoundError
else:
    torrentName = str(sys.argv[1])
    torrentCategory = str(sys.argv[2])
    torrentPath = max(glob(os.path.join(torrentSource, '*/')), key=os.path.getmtime)
    try:
        os.path.isdir(torrentPath)
    except FileNotFoundError:
        raise FileNotFoundError(f'Folder {torrentPath} can not be found')
    


if torrentCategory == 'other':
    OtherMover(torrentPath)
elif torrentCategory == 'tv' :
    TVMover(torrentPath)
    pass
elif torrentCategory == 'movies':
    prompt = f'''Reply only in JSON compatible text. Given the following torrent name: {torrentName} determine whether or not it's a movie, if it is a movie reply with the name and release year in JSON format as such
    {{
        "Name": "Die Hard",
        "Year":"1989"
    }}
    or if its not a movie reply with null values in the JSON file as such
    {{
        "Name": None,
        "Year": None
    }}
    '''
    apiReply = chatgpt(prompt)
    newName = f"{apiReply.get('name')} ({apiReply.get('year')})"
    MovieMover(newName)

else:
    prompt = f'''Reply only in JSON compatible text. Given the following torrent name: {torrentName} determine the name, release year and category of media as such
    {{
        "Name": "Die Hard",
        "Year":1989,
        "Category":"Movie"
    }}
    if it's a TV Show reply with the name, release year and category as such
    {{
        "Name": "Breaking Bad",
        "Year": 2008,
        "Category":"TV Show"
    }}
    if it's neither a movie or a tv show reply with null values as such
    {{
        "Name": None,
        "Year": None,
        "Category":None
    }}
    '''
    apiReply = chatgpt(prompt)
    # TODO: sort between movies tv other video files and non video files
    try:
        if 'movie' in str(apiReply.get('category')).lower():
            newName = apiReply.get('name')
            releaseYear = apiReply.get('year')
            MovieMover(torrentName, newName, releaseYear)
        elif 'tv' in str(apiReply.get('category')).lower():
            TVMover(torrentPath)
    except:
        OtherMover(torrentPath)
# # #

logging.info(f"Torrent '{torrentName}' successfully downloaded and managed!")