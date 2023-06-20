import requests

def getBearerToken():
    client_id = '24caaa8126be4477b94c2d360e9beac6'
    client_secret = '39a77a2dc7b74bb2996c983d4759749d'

    # Set the endpoint URL
    url = 'https://accounts.spotify.com/api/token'

    # Set the headers and data for the POST request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }

    # Send the POST request to obtain the token
    response = requests.post(url, headers=headers, data=data)

    # Process the response
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        # print(f'Bearer Token: {access_token}')
        return access_token
    else:
        print('Failed to obtain the bearer token.')
