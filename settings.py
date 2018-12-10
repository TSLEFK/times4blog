import os
from os.path import join, dirname, abspath
from dotenv import load_dotenv

# dotenv_path = join(dirname(dirname(abspath(__file__))), '.env')
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

slack_incoming_webhook_pass = os.environ.get("SLACK_WEBHOOK_URL")
SLACK_INCOMING_WEBHOOK_URL = "https://hooks.slack.com/services/" + slack_incoming_webhook_pass

slack_api_token = os.environ.get("SLACK_API_TOKEN")
slack_legacy_api_token = os.environ.get("LEGACY_SLACK_API_TOKEN")
slack_channel_id = os.environ.get("SLACK_CHANNEL_ID")
slack_channel_name = os.environ.get("SLACK_CHANNEL_NAME")

hatena_consumer_key = os.environ.get("Consumer_Key")
hatena_consumer_secret = os.environ.get("Consumer_Secret")
hatena_access_token = os.environ.get("Access_Token")
hatena_access_token_secret = os.environ.get("Access_Token_Secret")
hatena_id = os.environ.get("HATENA_ID")
hatena_password = os.environ.get("HATENA_PASSWORD")
