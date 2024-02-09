from openai_api.chatgpt import chatgpt
from openai import OpenAI

import logging
import os
import sys
import shutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('torrent-completed.log')
    ]
)

def MovieMover(current_torrent, new_name):
    movie_destination_folder = '/srv/maven/Media/Movies/'
    largest_file = max((os.path.join(root, file) for root, dirs, files in os.walk(current_torrent) for file in files),key=os.path.getsize)
    # MAKE IT COPY INSTEAD OF MOVE
    shutil.copy(os.path.join(current_torrent,largest_file), os.path.join(movie_destination_folder,new_name,largest_file))

    logging.info(f'Processed torrent {current_torrent} as Movie')
    Vacuum(current_torrent)
    pass

def TVMover(current_torrent):
    # MAKE IT NOT MOVE, BUT COPY TO ENSURE FILES GET LEFT IN SEEDING FOLDER
    os.system(f'tvnamer --config=/srv/maven/scripts/tvnamer/config.json --move --recursive --batch "{current_torrent}"')
    logging.info(f'Processed torrent {current_torrent} as TV')
    Vacuum(current_torrent)
    pass

def OtherMover(current_torrent):
    shutil.copytree(current_torrent, '/srv/maven/Torrents/Completed/')
    logging.info(f'Processed torrent {current_torrent} as Other')
    Vacuum(current_torrent)
    pass

def Vacuum(current_torrent):
    # cleaning function
    pass

seen_torrents = [list(line.strip('\n').split(',,,')) for line in open('torrent-seen.log','r').readlines()]

torrent_category = sys.argv[2]
path_to_seeding_torrent = sys.argv[3]

# find torrents in Seeding folder and add all to list seeding_torrents
seeding_torrents = os.listdir(path_to_seeding_torrent)
seeding_torrents = [os.path.join(path_to_seeding_torrent, f) for f in seeding_torrents] # add path to each file
seeding_torrents.sort(key=lambda x: os.path.getmtime(x))

f = open('torrent-seen.log', 'a')
for seeding_torrent in seeding_torrents[::-1]:
    seeding_torrent_date = os.path.getmtime(path_to_seeding_torrent)
    if set({seeding_torrent,{seeding_torrent_date}}) in seen_torrents:
        pass
    else:
        prompt = f'''Reply only in JSON compatible text. Given the following torrent name: {seeding_torrent.split('/')[-1]} determine the name, release year and category of media as such
        {{
            "Name": "Die Hard",
            "Year":1989,
            "Category":"Movie"
        }}
        if it's a TV Show reply with the name, season and category as such
        {{
            "Name": "Breaking Bad",
            "Season": 1,
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
        if 'movie' in apiReply.get('category').lower():
            MovieMover(seeding_torrent, f"{apiReply.get('name')} ({apiReply.get('year')})")
        elif 'tv' in apiReply.get('category').lower():
            TVMover(seeding_torrent)
        else:
            OtherMover(seeding_torrent)
        new_line = f'{seeding_torrent},,,{os.path.getmtime(seeding_torrent)}\n'
        print(new_line)
        f.write(new_line)
f.close()
