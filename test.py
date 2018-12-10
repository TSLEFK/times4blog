from slackclient import SlackClient
import settings

slack_token = settings.slack_api_token
sc = SlackClient(slack_token)

response = sc.api_call(
    "chat.postMessage",
    channel="channel id",
    text="Hello World from Python!"
)

print(response)
