import os
from datetime import datetime, timedelta
from slackclient import SlackClient
import settings
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel(os.getenv("LOGGER_LEVEL", "DEBUG"))

slack_token = settings.slack_api_token


def lambda_handler(event, context):
    sc = SlackClient(slack_token)
    oldest = datetime.today() - timedelta(days=1)
    oldest_timestamp = oldest.timestamp()

    # APIをたたく回数を減らすため、channel_idを優先
    slack_channel_id = settings.slack_channel_id
    if slack_channel_id == "":
        try:
            slack_channel_id = get_channel_id(sc)
        except ValueError as e:
            logger.error(e)
            return e

    response = sc.api_call(
        "channels.history",
        channel=slack_channel_id,
        oldest=oldest_timestamp,
    )  # type: dict

    if has_error_slack_response(response):
        return "response has error. :" + response["error"]

    for message in response["messages"]:
        print(message["text"])

    return "comp"


def get_channel_id(slack_client):
    if settings.slack_channel_name == "":
        raise ValueError("set channel id or name.")

    response_channels = slack_client.api_call(
        "channels.list"
    )  # type: dict

    if has_error_slack_response(response_channels):
        return "response has error. :" + response_channels["error"]

    for channel in response_channels["channels"]:
        if channel["name"] == settings.slack_channel_name:
            return channel["id"]

    raise ValueError("channel name {} is not found".format(settings.slack_channel_name))


def has_error_slack_response(response):
    """
    :param dict response:
    :return:
    """
    if response["ok"] == True:
        return False

    logger.error("response has error. : {}".format(response["error"]))

    if response["error"] == "missing_scope":
        logger.error("error(missing scope) detail is {} .".format(response["needed"]))

    return True


if __name__ == "__main__":
    res = lambda_handler("", "")
    print(res)
