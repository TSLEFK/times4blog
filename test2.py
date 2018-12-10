import oauth2 as oauth

import settings
from xml.sax.saxutils import *


def create_data(title, body):
    """
    :param title:
    :param body:
    :rtype bytes
    :return:
    """
    template = """
    <?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app">
        <title>{0}</title>
        <author><name>name</name></author>
        <content type="text/plain">{1}</content>
        <updated>2013-09-05T00:00:00</updated>
        <app:control>
            <app:draft>yes</app:draft>
        </app:control>
    </entry>
    """
    data = template.format(title, body).encode()
    return data


consumer = oauth.Consumer(settings.hatena_consumer_key, settings.hatena_consumer_secret)

token = oauth.Token(settings.hatena_access_token, settings.hatena_access_token_secret)
client = oauth.Client(consumer, token)

# 取得
resp, contents = client.request(uri='https://blog.hatena.ne.jp/satarn-sherlock/taskforce-hisui.hateblo.jp/atom/entry',
                                method="GET")
print(contents.decode())

data = create_data("test title", "test Body")

print(data)

print(type(data))
data_escaped = escape(data)

resp = client.request(uri='https://blog.hatena.ne.jp/satarn-sherlock/taskforce-hisui.hateblo.jp/atom/entry',
                      method="POST", body=data_escaped)
print(resp)
