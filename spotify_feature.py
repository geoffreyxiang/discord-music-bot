import requests
from spotify_auth import getBearerToken

# finds the id of the spotify playlist given by the link
def parseSpotifyLink(url):
    tokens = url.split("/")
    resIndex = -1
    for i in range(len(tokens)):
        if tokens[i] == "playlist":
            resIndex = i + 1
            break
    return tokens[resIndex] if resIndex > 0 else ""

def getPlayListInfo(url, bearerToken):
    id = parseSpotifyLink(url)
    api_url = f'https://api.spotify.com/v1/playlists/{id}'
    headers = {
        'Authorization': f'Bearer {bearerToken}',
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Failed to retrieve playlist information. Status code: {response.status_code}')
        return None

def getPlaylistQueue(response):
    tracksData = response['tracks']['items']
    res = []
    for item in tracksData:
        if not item['track'] or 'name' not in item['track']:
            continue
        name = item['track']['name']
        artist = item['track']['artists'][0]['name']
        res.append({ "name": name, "artist": artist })
    return res
    # return [{ "songName": item['track']['name'], "artist": item['track']['artists'][0]['name']} for item in tracksData]

def createPlaylist(url, bearerToken):
    response = getPlayListInfo(url, bearerToken)
    return getPlaylistQueue(response)