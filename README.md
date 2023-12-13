# Automatic Movie and TV Show torrent sorter
This sorter uses ChatGPT to sort through torrents and categorizes them as either a Movie or a TV Show. Outputs info to a .log file.

## Dependencies
For this to work some dependencies must first be installed. If using Docker, tvnamer, openai and thefuzz must be installed in the qbittorrent docker instance using the following commands:
>docker exec -it qbittorrent /bin/bash
>apk add py3-pip
>pip install tvnamer openai thefuzz

To check the logs:
>docker logs --follow qbittorrent