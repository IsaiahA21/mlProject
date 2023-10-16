# Author: Isaiah Asaolu
# Date: Oct/09/2023
# Description: The purpose of the program is to get the sentiment of the comments on a youtube video and store then them as postive, negative, or neutral.
# The program will then display the results in a pie chart.(If I have time)
# This is my first python project

import re
from tkinter import messagebox
import googleapiclient.discovery
import pandas as pandasImport

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer # for sentiment analysis. Install using pip install nltk

nltk_analyzer =SentimentIntensityAnalyzer()

#Graph library
from matplotlib import pyplot as plt
import numpy as numpy

#for user input window
from tkinter import *

# for getting the api key from your local environment variables
import os

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.environ.get("YOUTUBE_API_KEY")
if not DEVELOPER_KEY:
    messagebox.showinfo("Error", "Please set the variable YOUTUBE_API_KEY in your local environment variable.")

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY)



def save_to_file( vidTitle, resultsSize, mostPositive, mostNegative, data):
    vidTitle =vidTitle.replace(" ", "_")
    #write to file
    with open(f"Sentiment_Analysis{vidTitle}.txt", "w", encoding="utf-8") as file:
        file.write("Sentiment Analysis for video: " + vidTitle + "\n")
        file.write("There were " + str(resultsSize) + " comments extracted from the video." + "\n")
        file.write(str(data[0]) +" were positive comments, and " + str(data[1]) + " were negative comments.\n")
        
        file.write("The most positive comment was:  '" + mostPositive[0] + "'\nwith a compound score of "+ str(mostPositive[1]) + ".\n")
        file.write("The most negative comment was: '" + mostNegative[0]  + "'\n with a compound score of "+ str(mostNegative[1])+ ".\n")


def create_image(data, video_title, resultsSize):
     # creating a pie chart to represent the data
    mylabels = ["Positive", "Negative"]

    plt.pie(data,labels=mylabels, colors=["green","red"],  autopct=lambda p: f'{int(p * resultsSize / 100)} ({p:.1f}%)')
    plt.title("Sentiment Analysis {}".format(video_title))
    #save the chart
    video_title =video_title.replace(" ", "_")
    plt.savefig(f"Sentiment_Analysis{video_title}.png")
    plt.show()

def analyzeVideo(video_id):
    requestVidDetails = youtube.videos().list(
        part="snippet",
        id=video_id
    )

    video_title = None

    try:
        res = requestVidDetails.execute()


        # if there's 'item' and 'items' is not null
        if 'items' in res and res['items']:
            # Extract video title from response
            video_title = res['items'][0]['snippet']['title']
            print("Video Title: ", video_title)
        else:
            print("No video found with the provided ID: ", id)
            messagebox.showinfo(f"Video not found", "No video found with the provided ID. Please try different video")
            
    except Exception as e:
        messagebox.showerror("Error", "An error occured. Please try again.")
        print("An error occured: {e}")


    #Make a request for the youtube comments
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=1000,
        order="relevance",  # You can change this to orderUnspecified', 'time', 'relevance'
        textFormat = "plainText"

    )
    response = request.execute()

    commentsList = []

    resultsSize  = None
    resultsSize = response['pageInfo']['totalResults']


    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        commentsList.append([
            comment['authorDisplayName'],
            comment['publishedAt'],
            comment['updatedAt'],
            comment['likeCount'],
            comment['textDisplay']
        ])

    #want to sort the comments by the number of likes in descending order(most likes to least likes)
    # lambda comment: comment[3]: This lambda function takes a comment (which is a list), and returns the value of the fourth element in that list, i.e., comment[3]. This is the like_count of the comment.
    commentsList.sort(key=lambda commentsList: commentsList[3], reverse=True) 

    table_of_Comments = pandasImport.DataFrame(commentsList, columns=['author', 'published_at', 'updated_at', 'like_count', 'text'])
    commentsOnly = table_of_Comments['text']

    positiveCommentsCount = 0
    negativeCommentsCount = 0
    mostPositive = ["", -1] # mostPositive[0] is the string, mostPositive[1] is the score
    mostNegative = ["", 1]

    for comment in commentsOnly:
        sentiment_scores = nltk_analyzer.polarity_scores(comment)
        compound =sentiment_scores['compound']
        if compound >=0:
            positiveCommentsCount += 1
            if (compound > mostPositive[1]):
                mostPositive[0],mostPositive[1] = comment,compound
                
        else:
            negativeCommentsCount += 1
            if (compound < mostNegative[1]):
                mostNegative[0], mostNegative[1] = comment, compound
                
    data = [positiveCommentsCount,negativeCommentsCount]
    
    #create a pie chart and save it
    create_image(data, video_title, resultsSize)
    
    #write to comments file
    save_to_file(video_title, resultsSize, mostPositive, mostNegative,data)
    
    print("----------Analysis successful----------")


#*** processURL ***
# Example: Get the details of a video by its ID
# for Metro Boomin, Coi Leray - Self Love the youtube url is https://www.youtube.com/watch?v=yFruBMVvCZQ
# the id is the part after the ?v= so in this case yFruBMVvCZQ
# Make request to get video details
# youtube_url = "https://www.youtube.com/watch?v=yFruBMVvCZQ"

def processURL():
    youtube_url =entry.get()
    
    #check if the user entered a url
    if not youtube_url:
        messagebox.showinfo("Error", "Please enter a YouTube URL.")
        return
    
    # Check if the input is a valid YouTube URL
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_match = re.match(youtube_regex, youtube_url)
    
    # if the url is not valid
    if not youtube_match:
        messagebox.showinfo("Error", "Please enter a valid YouTube video URL.")
        return
    
    # valid youtube url
    video_id = youtube_url.split("v=")[1]
    analyzeVideo(video_id)

#****main code***

#The the url from the user
window = Tk()
# set the window width and height
window.geometry("300x350")

submit = Button(window, text="Submit",command=processURL)
#want to add a text saying enter the url
label_text = "Enter a Youtube url:"
label = Label(window, text=label_text)
label.pack()

entry = Entry(window, width=50, borderwidth=5)
entry.pack()

submit.pack()
window.mainloop()
