from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
from openai import Completion
from tweepy import OAuthHandler, API

load_dotenv()

app = Flask(__name__)

# Set up OpenAI API
openai.api_key = os.environ["OPENAI_API_KEY"]

# Set up Twitter API
consumer_key = os.environ["TWITTER_CONSUMER_KEY"]
consumer_secret = os.environ["TWITTER_CONSUMER_SECRET"]
access_token = os.environ["TWITTER_ACCESS_TOKEN"]
access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
twitter_api = tweepy.API(auth)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        article_url = request.form["article_url"]
        article_text = extract_article_text(article_url)
        summarized_points = summarize_article(article_text)
        twitter_thread = create_twitter_thread(summarized_points)
        return redirect(url_for("index"))

    return render_template("index.html")

def extract_article_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    article_text = "\n".join([p.get_text() for p in paragraphs])
    return article_text

def summarize_article(article_text):
    prompt = f"Summarize the following article into key points:\n\n{article_text}\n\nKey Points:"
    response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=150, n=1, stop=None, temperature=0.7)
    key_points = response.choices[0].text.strip().split("\n")
    return key_points

def create_twitter_thread(points):
    prev_tweet_id = None
    for point in points:
        tweet = twitter_api.update_status(status=point[:280], in_reply_to_status_id=prev_tweet_id, auto_populate_reply_metadata=True)
        prev_tweet_id = tweet.id
