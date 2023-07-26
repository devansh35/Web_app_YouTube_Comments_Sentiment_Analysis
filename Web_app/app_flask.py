from flask import Flask, request, jsonify
from flask_cors import CORS
from itertools import islice
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
import pandas as pd
import pickle
import re
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from string import punctuation
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer

app = Flask(__name__)
CORS(app)

# Load the trained Naive Bayes model from a file
with open('naive_bayes_model.pkl', 'rb') as f:
    classifier = pickle.load(f)

# Load the trained Count Vectorizer model from a file
with open('count_vectorizer_model.pkl', 'rb') as f:
    cv = pickle.load(f)    


stopwords_en = set(stopwords.words('english'))
lzr = WordNetLemmatizer()

# Create a function to preprocess text
def text_processing(text):
    text = text.lower()
    text = re.sub(r'\n',' ', text)
    text = re.sub('[%s]' % re.escape(punctuation), "", text)
    text = re.sub("^a-zA-Z0-9$,.", "", text)
    text = re.sub(r'\s+', ' ', text, flags=re.I)
    text = re.sub(r'\W', ' ', text)
    text = ' '.join([word for word in word_tokenize(text) if word not in stopwords_en])
    text = ' '.join([lzr.lemmatize(word) for word in word_tokenize(text)])
    return text

# Create a function to download and preprocess YouTube comments
def download_and_preprocess_comments(video_link):
    downloader = YoutubeCommentDownloader()
    data = []
    try:
        comments = downloader.get_comments_from_url(video_link, sort_by=SORT_BY_POPULAR)
        for comment in islice(comments, 1000):
            data.append(comment)
    except:
        return None
    df = pd.DataFrame(data, columns=['text'])
    df['text'] = df['text'].apply(text_processing)
    return df

# Create an endpoint for the web app to send a YouTube video link and get the sentiment analysis result
@app.route('/predict_sentiment', methods=['POST'])
def predict_sentiment():
    video_link = request.form.get('video_link')
    if not video_link:
        return jsonify({'error': 'No video link provided.'})
    df = download_and_preprocess_comments(video_link)
    if df is None or df.empty:
        return jsonify({'error': 'Error downloading or processing comments.'})
    X = cv.transform(df['text']).toarray()
    y_pred = classifier.predict(X)
    sentiment_counts = pd.Series(y_pred).value_counts().to_dict()

    # Get the sentiment with maximum count
    max_sentiment = max(sentiment_counts, key=sentiment_counts.get)

    # Map the sentiment to its corresponding label
    sentiment_label = {
        0: "Negative",
        1: "Neutral",
        2: "Positive"
    }

    # Return the sentiment label with maximum count
    return jsonify(sentiment_label[max_sentiment])


if __name__ == '__main__':
    app.run(debug=True)