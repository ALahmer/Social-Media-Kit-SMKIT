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

## Configuring the Environment File (`env.json`)

To use the Social Media Kit (SMKIT) effectively, you must properly configure the environment file (`env.json`) to specify paths and settings for web post generation and module configuration.

**Start by making a copy of the provided `env_sample.json` file and renaming it to `env.json`.*** 

### Environment Fields

Below is a description of each required field and its purpose:

#### **Global Configuration Fields**

- **`web_posts_absolute_destination_path`**:  
  Specifies the absolute filesystem path where the generated web pages will be stored.  
  *Example:*  
  `"web_posts_absolute_destination_path": "/var/www/negapedia/en/html/smkitwebpages/"`  

- **`posts_images_absolute_destination_path`**:  
  Specifies the absolute filesystem path where the images associated with posts will be stored.  
  *Example:*  
  `"posts_images_absolute_destination_path": "/var/www/negapedia/images/"`  

#### **Module-Specific Configuration**

Modules can have specific configurations to handle particular needs. Each module will have its own key in the `modules` section, containing settings relevant to that module.

- **`modules`**:  
  A dictionary containing configuration settings for each module.

##### **Generic Module Configuration (`generic`)**

- **`filesystem_website_base_directory`**: The default absolute filesystem path from which local pages are being processed, this configuration is taken if no parameter in `--base_directory` is specified.  
  *Example:* `"filesystem_website_base_directory": "/var/www/mywebsite/en/html"`

- **`website_base_url`**: The default base URL from which the web pages to analyse are being generated, this configuration is taken if no parameter in `--base_url` is specified.  
  *Example:* `"website_base_url": "https://en.mywebsite.org"`

##### **Negapedia Module Configuration (`negapedia`)**

- **`filesystem_website_base_directory`**: The default absolute filesystem path from which local pages are being processed, this configuration is taken if no parameter in `--base_directory` is specified.  
  *Example:* `"filesystem_website_base_directory": "/var/www/negapedia/en/html"`

- **`website_base_url`**: The default base URL from which the web pages to analyse are being generated, this configuration is taken if no parameter in `--base_url` is specified.  
  *Example:* `"website_base_url": "http://en.negapedia.org"`

- **`number_of_words_that_matter_to_extract`**:  
  The default number of "words that matter" to extract from the content for analysis, this configuration is taken if no parameter in `--number_of_words_that_matter_to_extract` is specified.  
  *Example:* `"number_of_words_that_matter_to_extract": 3`

- **`number_of_conflict_awards_to_extract`**:  
  The default number of conflict awards to extract for analysis, this configuration is taken if no parameter in `--number_of_conflict_awards_to_extract` is specified.  
  *Example:* `"number_of_conflict_awards_to_extract": 3`

- **`number_of_polemic_awards_to_extract`**:  
  The default number of polemic awards to extract for analysis, this configuration is taken if no parameter in `--number_of_polemic_awards_to_extract` is specified.  
  *Example:* `"number_of_polemic_awards_to_extract": 3`

- **`number_of_social_jumps_to_extract`**:  
  The default number of social jumps to extract for analysis, this configuration is taken if no parameter in `--number_of_social_jumps_to_extract` is specified.  
  *Example:* `"number_of_social_jumps_to_extract": 3`

##### **Facebook Parameters**
  - `facebook_app_id`: Your Facebook App ID.
  - `facebook_app_secret`: Your Facebook App Secret.
  - `facebook_page_id`: Your Facebook Page ID.
  - `facebook_short_lived_user_access_token`: A Short Lived User Access Token.
  - `facebook_long_lived_page_access_token`: A Long Lived Page Access Token (generated by the tool).

##### **Twitter Parameters**
  - `twitter_api_key`: Your Twitter API Key.
  - `twitter_api_secret_key`: Your Twitter API Secret Key.
  - `twitter_access_token`: Your Twitter Access Token.
  - `twitter_access_token_secret`: Your Twitter Access Token Secret.

### Important Notes

- All fields mentioned above must be set correctly for the tool to function as expected.
- Ensure that the specified paths are accessible and have the necessary permissions to allow read/write operations.
- The URLs provided must be publicly accessible if they are meant to be used in a web context.
- Make sure to maintain the correct structure of the `env.json` file to avoid parsing errors.

---

## Configuring the Environment File (`env.json`)

To use the Social Media Kit (SMKIT) effectively, you must properly configure the environment file (`env.json`) to specify paths and settings for web post generation and module configuration.

### Environment Fields

Below is a description of each required field and its purpose:

#### **Global Configuration Fields**

- **`web_posts_absolute_destination_path`**:  
  Specifies the absolute filesystem path where the generated web pages will be stored.  
  *Example:*  
  `"web_posts_absolute_destination_path": "/var/www/negapedia/en/html/smkitwebpages/"`  

- **`posts_images_absolute_destination_path`**:  
  Specifies the absolute filesystem path where the images associated with posts will be stored.  
  *Example:*  
  `"posts_images_absolute_destination_path": "/var/www/negapedia/images/"`  

#### **Module-Specific Configuration**

Modules can have specific configurations to handle particular needs. Each module will have its own key in the `modules` section, containing settings relevant to that module.

- **`modules`**:  
  A dictionary containing configuration settings for each module.

##### **Generic Module Configuration (`generic`)**

- **`filesystem_website_base_directory`**: The default absolute filesystem path from which local pages are being processed, this configuration is taken if no parameter in `--base_directory` is specified.  
  *Example:* `"filesystem_website_base_directory": "/var/www/mywebsite/en/html"`

- **`website_base_url`**: The default base URL from which the web pages to analyse are being generated, this configuration is taken if no parameter in `--base_url` is specified.  
  *Example:* `"website_base_url": "https://en.mywebsite.org"`

##### **Negapedia Module Configuration (`negapedia`)**

- **`filesystem_website_base_directory`**: The default absolute filesystem path from which local pages are being processed, this configuration is taken if no parameter in `--base_directory` is specified.  
  *Example:* `"filesystem_website_base_directory": "/var/www/negapedia/en/html"`

- **`website_base_url`**: The default base URL from which the web pages to analyse are being generated, this configuration is taken if no parameter in `--base_url` is specified.  
  *Example:* `"website_base_url": "http://en.negapedia.org"`

- **`number_of_words_that_matter_to_extract`**:  
  The default number of "words that matter" to extract from the content for analysis, this configuration is taken if no parameter in `--number_of_words_that_matter_to_extract` is specified.  
  *Example:* `"number_of_words_that_matter_to_extract": 3`

- **`number_of_conflict_awards_to_extract`**:  
  The default number of conflict awards to extract for analysis, this configuration is taken if no parameter in `--number_of_conflict_awards_to_extract` is specified.  
  *Example:* `"number_of_conflict_awards_to_extract": 3`

- **`number_of_polemic_awards_to_extract`**:  
  The default number of polemic awards to extract for analysis, this configuration is taken if no parameter in `--number_of_polemic_awards_to_extract` is specified.  
  *Example:* `"number_of_polemic_awards_to_extract": 3`

- **`number_of_social_jumps_to_extract`**:  
  The default number of social jumps to extract for analysis, this configuration is taken if no parameter in `--number_of_social_jumps_to_extract` is specified.  
  *Example:* `"number_of_social_jumps_to_extract": 3`

### Important Notes

- All fields mentioned above must be set correctly for the tool to function as expected.
- Ensure that the specified paths are accessible and have the necessary permissions to allow read/write operations.
- The URLs provided must be publicly accessible if they are meant to be used in a web context.
- Make sure to maintain the correct structure of the `env.json` file to avoid parsing errors.

---

## Setting Up Facebook Connector

To initialize the Facebook connector, you need to populate several environment variables in the `env.json` file, including the `facebook_app_id`, `facebook_app_secret`, `facebook_page_id` and `facebook_short_lived_user_access_token`.

### Steps to Retrieve Facebook Credentials

1. **Create a Facebook App**:
   - Visit the [Facebook for Developers](https://developers.facebook.com/apps/?locale=en_US) page.
   - Click on **"Create App"** and follow the prompts to set up your app. This will generate your **`facebook_app_id`** and **`facebook_app_secret`**.
   - You can find these credentials in your app's **Dashboard** under **Settings > Basic**.

2. **Generate a Short-Lived User Access Token and Retrieve the Page ID**:
   - Go to the [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/).
   - Select your app from the dropdown menu.
   - Ensure **"User Token"** is selected under the **User or Page** option.
   - Ensure the required permissions are granted:
     - `pages_read_engagement`
     - `pages_show_list`
     - `pages_manage_posts`
   - Click on **"Generate Access Token"**. This will generate a short-lived user access token.
   - Copy this token and add it to your `env.json` under `"facebook_short_lived_user_access_token"`.
   - In the Facebook Graph API Explorer, make a request to the `/me/accounts` endpoint:
   - The response will include a list of pages you manage, along with their respective **`id`**.
   Example response from `/me/accounts`:

   ```json
   {
     "data": [
       {
         "access_token": "",
         "category": "",
         "category_list": [...],
         "name": "PAGE_NAME",
         "id": "PAGE_ID",
         "tasks": [...]
       }
     ]...
   }
   ```
   - Copy your id and add it to your `env.json` under `"facebook_page_id"`.


   ⚠️ **Warning:** If the long-lived token is not used for approximately 60 days, it may expire and become non-refreshable. In this case, you must clear the existing token from the `env.json` file and [obtain a new short-lived access token](#generate-a-short-lived-user-access-token-and-retrieve-the-page-id) to continue using the tool. ⚠️

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

## Usage

SMKIT can be run from the command line. Below are examples of how to use it with different modules and modes:

### Generic Module (Mode: Summary)

```sh
python smkit.py --mode summary --pages "https://example.com/page1" --post_type "twitter" "facebook"
```
*practical example*:
```sh
python smkit.py --mode summary --pages "https://techcrunch.com/2024/08/10/after-global-it-meltdown-crowdstrike-courts-hackers-with-action-figures-and-gratitude/" --post_type "web" "twitter" "facebook"
```

### Negapedia Module (Mode: Summary)

```sh
python smkit.py --module negapedia --mode summary --pages "https://negapedia.org/articles/TopicA" --language "en" --post_type "web"
```
*practical example*:
```sh
python smkit.py --module negapedia --mode summary --pages "http://en.negapedia.org/articles/George_W._Bush" --language "en" --post_type "web" "twitter" "facebook"
```

### Negapedia Module (Mode: Comparison)

```sh
python smkit.py --module negapedia --mode comparison --pages "https://negapedia.org/articles/TopicA" "https://negapedia.org/articles/TopicB" --language "it" --post_type "facebook" "twitter"
```
*practical example*:
```sh
python smkit.py --module negapedia --mode comparison --pages "http://en.negapedia.org/articles/George_W._Bush" "http://en.negapedia.org/articles/Barack_Obama" --language "it" --post_type "web" "facebook" "twitter"
```

### Negapedia Module (Mode: Ranking)

```sh
python smkit.py --module negapedia --mode ranking --pages "/var/www/negapedia/en/html/news/" --language "en" --post_type "web" --ranking_fields "recent_conflict_levels" "recent_polemic_levels"
```
*practical example*:
```sh
python smkit.py --module negapedia --mode ranking --pages "http://it.negapedia.org/articles/Atalanta_Bergamasca_Calcio" "http://it.negapedia.org/articles/Bologna_Football_Club_1909" "http://it.negapedia.org/articles/Cagliari_Calcio" "http://it.negapedia.org/articles/Empoli_Football_Club" "http://it.negapedia.org/articles/ACF_Fiorentina" "http://it.negapedia.org/articles/Frosinone_Calcio" "http://it.negapedia.org/articles/Genoa_Cricket_and_Football_Club" "http://it.negapedia.org/articles/Football_Club_Internazionale_Milano" "http://it.negapedia.org/articles/Juventus_Football_Club" "http://it.negapedia.org/articles/Societ%C3%A0_Sportiva_Lazio" "http://it.negapedia.org/articles/Unione_Sportiva_Lecce" "http://it.negapedia.org/articles/Associazione_Calcio_Milan" "http://it.negapedia.org/articles/Associazione_Calcio_Monza" "http://it.negapedia.org/articles/Societ%C3%A0_Sportiva_Calcio_Napoli" "http://it.negapedia.org/articles/Associazione_Sportiva_Roma" "http://it.negapedia.org/articles/Unione_Sportiva_Salernitana_1919" "http://it.negapedia.org/articles/Unione_Sportiva_Sassuolo_Calcio" "http://it.negapedia.org/articles/Torino_Football_Club" "http://it.negapedia.org/articles/Udinese_Calcio" "http://it.negapedia.org/articles/Hellas_Verona_Football_Club" --language "it" --post_type "web" "facebook" "twitter"
```

---
