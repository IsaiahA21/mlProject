import os
from googleapiclient.discovery import build

# Set your API key here
api_key = 'AIzaSyBrA337xLuDmUEsEZkpHi7B_jv3_XjfvPY'

# Create a YouTube Data API service
myYoutube = build('youtube', 'v3', developerKey=api_key)

# Example: Get the details of a video by its ID
# for baby by justin bieber the youtube url is https://www.youtube.com/watch?v=yFruBMVvCZQ
# the id is the part after the ?v= so in this case yFruBMVvCZQ
video_id = 'yFruBMVvCZQ'
request = myYoutube.videos().list(
    part='snippet',
    id=video_id
)

response = request.execute()

# Print the response (you might want to do something more meaningful with it)
# print(response)

title = response['items'][0]['snippet']['title']
print(title)
