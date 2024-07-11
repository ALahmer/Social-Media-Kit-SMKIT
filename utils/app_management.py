import subprocess
from flask import Flask, request, redirect, session, url_for
import requests
import facebook
from utils.env_management import load_from_env, save_to_env

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your own secret key


env_data = load_from_env()
facebook_app_id = env_data['facebook_app_id']
facebook_app_secret = env_data['facebook_app_secret']
facebook_redirect_uri = env_data['facebook_redirect_uri']


# Step 1: Redirect to Facebook for authorization
@app.route('/')
def index():
    auth_url = (
        f"https://www.facebook.com/v12.0/dialog/oauth?client_id={facebook_app_id}&redirect_uri={facebook_redirect_uri}&scope=pages_read_engagement,pages_manage_posts"
    )
    return redirect(auth_url)


# Step 2: Handle the callback from Facebook
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = (
        f"https://graph.facebook.com/v12.0/oauth/access_token?client_id={facebook_app_id}&redirect_uri={facebook_redirect_uri}&client_secret={facebook_app_secret}&code={code}"
    )
    response = requests.get(token_url)
    access_token_info = response.json()
    user_access_token = access_token_info['access_token']

    # Store the user access token in session
    session['user_access_token'] = user_access_token

    return redirect(url_for('get_page_access_token'))


# Step 3: Exchange User Access Token for Page Access Token
@app.route('/get_page_access_token')
def get_page_access_token():
    user_access_token = session.get('user_access_token')
    if not user_access_token:
        return redirect(url_for('index'))

    graph = facebook.GraphAPI(user_access_token)
    pages_data = graph.get_object('/me/accounts')
    pages = pages_data['data']

    # Get the first page's access token
    if pages:
        page_access_token = pages[0]['access_token']
        env_data['page_access_token'] = page_access_token
        save_to_env(env_data)
        return "Access token saved successfully. You can close this window."
    else:
        return "No pages found."

def start_flask_app():
    print("Starting Flask server for authentication...")
    subprocess.Popen(['python', 'app.py'])

if __name__ == '__main__':
    app.run(debug=True)
