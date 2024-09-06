# Social Media Kit (SMKIT)

SMKIT is a versatile tool designed to automate the management of content across various social media platforms and websites. It provides functionality for extracting metadata, creating custom templates posts.

---

## Features

- **Automated Content Posting**: Post content to social media platforms like Facebook, Twitter, etc.
- **Metadata Extraction**: Extract Open Graph and standard HTML meta tags for efficient content sharing.
- **Custom Templates**: Use pre-designed templates to ensure consistent branding across platforms.
- **Cross-Platform Integration**: Manage multiple social media accounts from a single platform.

---

## Installation

To get started with SMKIT, clone the repository and install the required dependencies:

```bash
git clone https://github.com/ALahmer/Social-Media-Kit-SMKIT.git
cd Social-Media-Kit-SMKIT
pip install -r requirements.txt
```

---

## Requirements

Ensure you have Python installed (***version 3.6 or higher***) and install the following dependencies:

```bash
    requests~=2.31.0
    matplotlib~=3.6.0
    seaborn~=0.13.2
    beautifulsoup4~=4.12.3
    tweepy~=4.14.0
    facebook-sdk~=3.1.0
    filetype~=1.2.0
    colorlog~=6.8.2
    Pillow~=9.2.0
    CairoSVG~=2.7.1
```

Install dependencies with:
```bash
pip install -r requirements.txt
```

---

## Usage

SMKIT can be run from the command line. Below are examples of how to use it with different modules and modes:

### Generic Module (Mode: Summary)

```sh
python smkit.py --mode summary --pages "https://example.com/page1" --post_type "twitter" "facebook"
```

### Negapedia Module (Mode: Summary)

```sh
python smkit.py --module negapedia --mode summary --pages "https://negapedia.org/articles/TopicA" --language "en" --post_type "web"
```

### Negapedia Module (Mode: Comparison)

```sh
python smkit.py --module negapedia --mode comparison --pages "https://negapedia.org/articles/TopicA" "https://negapedia.org/articles/TopicB" --language "it" --post_type "facebook" "twitter"
```

### Negapedia Module (Mode: Ranking)

```sh
python smkit.py --module negapedia --mode ranking --pages "/var/www/negapedia/en/html/news/" --language "en" --post_type "web" --ranking_fields "recent_conflict_levels" "recent_polemic_levels"
```

---

## Command-Line Arguments

The `smkit` tool accepts a variety of command-line arguments to control its behavior and specify the input data. Below is a description of each argument:

- `--module`: *(Optional)* The module to use for processing. Examples include `generic` or `negapedia`. Default is `generic`.
- `--pages`: *(Required)* One or more URLs or file paths to be processed. Multiple values can be specified by separating them with spaces.
- `--mode`: *(Required)* Specifies the mode of analysis. Valid options are:
  - `summary`: Generate a summary of the input pages.
  - `comparison`: Compare two input pages. Exclusive for `negapedia` module.
  - `ranking`: Create a ranking based on the selected criteria. Exclusive for `negapedia` module.
- `--post_type`: *(Optional)* Specifies the type of post to create. Valid options are `twitter`, `facebook`, and `web`. You can choose one or more platforms by separating them with spaces.
- `--message`: *(Optional)* A custom message to include in the post. If not provided, a build one will be generated based on the content.
- `--language`: *(Optional)* The language in which to create the post. Options are `en` (English) or `it` (Italian). Default is `en`.
- `--minimum_article_modified_date`: *(Optional)* A filter for pages based on their last modified date. Only pages modified on or after this date (in `YYYY-MM-DD` format) will be processed. Exclusive for `generic` module.
- `--base_directory`: *(Optional)* Specifies the filesystem base directory for websites. Used when input paths are local files.
- `--base_url`: *(Optional)* Specifies the base URL for websites. Used to map local paths to web URLs.
- `--remove_suffix`: *(Optional)* A flag to indicate whether `.html` or `.htm` suffixes should be removed from URLs.
- `--number_of_words_that_matter_to_extract`: *(Optional)* Number of important words to extract for analysis. Exclusive for `negapedia` module.
- `--number_of_conflict_awards_to_extract`: *(Optional)* Number of conflict awards to extract for analysis. Exclusive for `negapedia` module.
- `--number_of_polemic_awards_to_extract`: *(Optional)* Number of polemic awards to extract for analysis. Exclusive for `negapedia` module.
- `--number_of_social_jumps_to_extract`: *(Optional)* Number of social jumps to extract for analysis. Exclusive for `negapedia` module.
- `--ranking_fields`: *(Optional)* Fields to use for ranking. Choices are `recent_conflict_levels`, `recent_polemic_levels`, `mean_conflict_level`, and `mean_polemic_level`. If not specified, all fields will be used for ranking.

Each argument allows you to customize the behavior of `smkit` to suit your needs, whether it's generating summaries, comparisons, or rankings, or targeting specific social media platforms for posting.

---

## Setting Up the Environment File

To properly configure the SMKIT tool, you need to set up an environment file named `env.json` that contains the necessary authentication parameters for both Facebook and Twitter. Start by making a copy of the provided `env_sample.json` file and renaming it to `env.json`. 

After renaming, open the `env.json` file and populate it with the following required fields:

- **Facebook Parameters:**
  - `facebook_app_id`: Your Facebook App ID.
  - `facebook_app_secret`: Your Facebook App Secret.
  - `facebook_page_access_token`: A Page Access Token.

- **Twitter Parameters:**
  - `twitter_api_key`: Your Twitter API Key.
  - `twitter_api_secret_key`: Your Twitter API Secret Key.
  - `twitter_access_token`: Your Twitter Access Token.
  - `twitter_access_token_secret`: Your Twitter Access Token Secret.

An example of a properly configured `env.json` file:

```json
{
  "facebook_app_id": "YOUR_FACEBOOK_APP_ID",
  "facebook_app_secret": "YOUR_FACEBOOK_APP_SECRET",
  "facebook_page_access_token": "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN",
  "twitter_api_key": "YOUR_TWITTER_API_KEY",
  "twitter_api_secret_key": "YOUR_TWITTER_API_SECRET_KEY",
  "twitter_access_token": "YOUR_TWITTER_ACCESS_TOKEN",
  "twitter_access_token_secret": "YOUR_TWITTER_ACCESS_TOKEN_SECRET"
}
```

Make sure to keep the `env.json` file secure, as it contains sensitive information necessary for SMKIT to authenticate and interact with the social media platforms.

---

## Setting Up Facebook Connector

To initialize the Facebook connector, you need to populate several environment variables in the `env.json` file, including the `facebook_app_id`, `facebook_app_secret`, and `facebook_page_access_token`. 

### Steps to Retrieve Facebook Credentials

1. **Create a Facebook App**:
   - Visit the [Facebook for Developers](https://developers.facebook.com/apps/) page.
   - Click on **"Create App"** and follow the prompts to set up your app. This will generate your **`facebook_app_id`** and **`facebook_app_secret`**.
   - You can find these credentials in your app's **Dashboard** under **Settings > Basic**.

2. **Generate a Page Access Token**:
   - Go to the [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/).
   - Select your app from the dropdown menu.
   - Generate a User Access Token with the required permissions (`pages_read_engagement`, **`pages_show_list`**, `pages_manage_posts`).
   - Use this access token to call the `/me/accounts` endpoint to retrieve the **`facebook_page_access_token`** for your Facebook Page.

3. **Set Up Your `env.json` File**:
   - Open your `env.json` file and enter the retrieved values:

Example `env.json`:

```json
{
  "facebook_app_id": "YOUR_FACEBOOK_APP_ID",
  "facebook_app_secret": "YOUR_FACEBOOK_APP_SECRET",
  "facebook_page_access_token": "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN",
}
```
Make sure to keep the `env.json` file secure, as it contains sensitive information necessary for SMKIT to authenticate and interact with the social media platforms.

---

## Setting Up Twitter Connector

To initialize the Twitter connector, you need to populate several environment variables in the `env.json` file, including the `twitter_api_key`, `twitter_api_secret_key`, `twitter_access_token`, and `twitter_access_token_secret`.

### Steps to Retrieve Twitter Credentials

1. **Create a Twitter Developer Account**:
   - Visit the [Twitter Developer Platform](https://developer.twitter.com/) and log in with your Twitter account.
   - If you don't have a developer account, you'll need to apply for one and provide the necessary details about your intended use.

2. **Create a Twitter App**:
   - Once your developer account is approved, go to the [Developer Dashboard](https://developer.twitter.com/en/apps) and click on **"Create App"**.
   - Fill in the required details for your application. After creation, you will find the **`twitter_api_key`** and **`twitter_api_secret_key`** in the **Keys and Tokens** tab of your app settings.

3. **Generate Access Tokens**:
   - In the **Keys and Tokens** tab, scroll down to the **Access Token & Secret** section.
   - Click on **"Generate"** to create your **`twitter_access_token`** and **`twitter_access_token_secret`**. Ensure that you have the correct permissions for the actions you want to perform (e.g., read and write access).

4. **Set Up Your `env.json` File**:
   - Open your `env.json` file and enter the retrieved values:

Example `env.json`:

```json
{
  "twitter_api_key": "YOUR_TWITTER_API_KEY",
  "twitter_api_secret_key": "YOUR_TWITTER_API_SECRET_KEY",
  "twitter_access_token": "YOUR_TWITTER_ACCESS_TOKEN",
  "twitter_access_token_secret": "YOUR_TWITTER_ACCESS_TOKEN_SECRET",
}
```
Make sure to keep the `env.json` file secure, as it contains sensitive information necessary for SMKIT to authenticate and interact with the social media platforms.

---
