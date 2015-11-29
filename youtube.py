import sys
from apiclient.discovery import build
from apiclient.errors import HttpError

import config


def youtube_search(album, artist, track):
    youtube = build('youtube', 'v3', developerKey=config.GOOGLE_API_KEY)

    search_response = youtube.search().list(
        q = album + ' ' + artist + ' ' + track,
        part = 'id,snippet',
        order = 'relevance',
        videoDuration = 'short',
        type = 'video',
        maxResults = 10
    ).execute()

    videos = []
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            videos.append((search_result['snippet']['title'], search_result['id']['videoId']))

    return videos


if __name__ == '__main__':
    try:
        youtube_search(sys.argv[1], sys.argv[2], sys.argv[3])
    except HttpError as e:
        print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))