import requests
from time import time
import get_signature_util
from urllib import parse

import settings


def create_oauth_header(oauth_params):
    """
    キーと値の辞書から、OAuthのHTTPヘッダ用の文字列を作成します。
    Args:
        oauth_params: HTTPヘッダ "OAuth" に付与するキーと値の辞書
    Returns:
        OAuthHTTPヘッダ文字列
    """

    auth_header_entries = []
    for key, value in oauth_params.items():
        auth_header_entries.append("%s=\"%s\"" % (key, value))

    return "OAuth " + ",".join(auth_header_entries)


def get_request_token(consumer_key, consumer_secret, scope):
    """
    consumer_key, consumer_secretから、request_tokenを取得する。
    Args:
        consumer_key: 事前にはてなにアプリケーション登録して取得したConsumer Key文字列. URLエンコードされていない値を渡すこと
        consumer_secret: 事前にはてなにアプリケーション登録して取得したConsumer Secret文字列. URLエンコードされていない値を渡すこと
        scope: 取得したいアクセストークンのscopeをコンマでつないだ文字列. URLエンコード等されていない値を渡すこと
            e.x. "read_public,read_private,write_public,write_private"
    Returns:
        取得したrequest_tokenとrequest_token_secret情報.
        {"request_token" : request_token, "request_token_secret": request_token_secret } の構造の辞書データ
    """

    nonce = "0c670efea71547422662"
    timestr = str(int(time()))

    request_url = 'https://www.hatena.com/oauth/initiate'
    http_method = 'post'

    # HeaderのAuthorizationパラメータに含める値
    # oauth_signatureはこれから作成するのでまだなし
    oauth_params = {
        'realm': '',
        'oauth_callback': 'oob',
        'oauth_consumer_key': consumer_key,
        'oauth_nonce': nonce,
        'oauth_signature': None,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': timestr
    }

    # Authorizationパラメータからoauthで始まるパラメータでNoneでないものを抽出
    q_params = {}
    [q_params.update({k: v}) for k, v in oauth_params.items()
     if k.startswith('oauth') if v is not None]

    # 送信するデータをパラメータに追加する
    send_data = {'scope': 'read_public,read_private,write_public,write_private'}
    q_params.update(send_data)

    # ハッシュを計算するkeyとdataを生成し、signature計算
    signature = get_signature_util.make_signature(consumer_secret, 'post', request_url, q_params)

    oauth_params["oauth_signature"] = signature

    # request_token取得
    response = requests.post(request_url, headers={"Authorization": create_oauth_header(oauth_params),
                                                   "Content-Type": "application/x-www-form-urlencoded"},
                             params=send_data).content

    request_token = response.decode().split("oauth_token=")[1].split("&")[0]
    request_token_secret = response.decode().split("oauth_token_secret=")[1].split("&")[0]

    return {"request_token": parse.unquote(request_token), "request_token_secret": parse.unquote(request_token_secret)}


def get_rk(hatena_id, password):
    """はてなIDとログインパスワードからrkを取得します。
    rkが何なのかはよく分からない。
    Args:
        hatena_id:  はてなID文字列
        password: はてなIDに対応するはてなログイン用のパスワード
    Returns:
        rk文字列
    Raises:
        KeyError: rk文字列が取得できなかったとき。ID/パスワードが間違っているか、rkを取得するためのはてなAPIの仕様が変わった
    """
    target_url = "https://www.hatena.ne.jp/login"
    payload = {'name': hatena_id, 'password': password}
    response = requests.post(target_url, data=payload)

    try:
        rk = response.headers["Set-Cookie"].split("rk=")[1].split(";")[0]
    except IndexError:
        raise KeyError(
            "cannot get rk using hatena_id: %s and password: %s . ID/Password is wrong, or Hatena API spec changed." % (
                hatena_id, password))
    return rk


def get_verifier_code(request_token, hatena_id, password):
    rk = get_rk(hatena_id, password)

    response = requests.get("https://www.hatena.ne.jp/oauth/authorize?oauth_token=" + parse.quote(request_token),
                            headers={"Cookie": "rk=" + rk}).content
    # responseから強引にrkmの値を取り出す   
    rkm = response.decode().split("<input type=\"hidden\" name=\"rkm\" value=\"")[1].split("\"")[0]

    # request_tokenとrkmの値を使って、アプリ認証を許可した相当の操作を行う
    response = requests.post("https://www.hatena.ne.jp/oauth/authorize", headers={"Cookie": "rk=" + rk},
                             params={"rkm": rkm, "oauth_token": request_token,
                                     "name": "%E8%A8%B1%E5%8F%AF%E3%81%99%E3%82%8B"}).content

    # responseから強引にverifierの値を取り出す
    verifier = response.decode().split("<div class=verifier><pre>")[1].split("<")[0]

    return verifier


def get_access_token(consumer_secret, request_token, request_token_secret, oauth_verifier_code):
    nonce = "TekitouNaMojidesun"
    timestr = str(int(time()))

    request_url = 'https://www.hatena.com/oauth/token'
    http_method = 'post'

    # HeaderのAuthorizationパラメータに含める値
    # oauth_signatureはこれから作成するのでまだなし
    oauth_params = {
        'realm': '',
        'oauth_consumer_key': consumer_key,
        'oauth_nonce': nonce,
        'oauth_signature': None,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': timestr,
        'oauth_token': request_token,
        'oauth_verifier': oauth_verifier_code,
        'oauth_version': '1.0'
    }

    # Authorizationパラメータからoauthで始まるパラメータでNoneでないものを抽出
    q_params = {}
    [q_params.update({k: v}) for k, v in oauth_params.items()
     if k.startswith('oauth') if v is not None]

    signature = get_signature_util.make_signature(consumer_secret, 'post', request_url, q_params, request_token_secret)

    oauth_params["oauth_signature"] = signature

    response = requests.post(request_url, headers={"Authorization": create_oauth_header(oauth_params),
                                                   "Content-Type": "application/x-www-form-urlencoded"}).content

    access_token = response.decode().split("oauth_token=")[1].split("&")[0]
    access_token_secret = response.decode().split("oauth_token_secret=")[1].split("&")[0]

    return {"oauth_token": parse.unquote(access_token), "oauth_token_secret": parse.unquote(access_token_secret)}


if __name__ == "__main__":
    hatena_id = settings.hatena_id
    password = settings.hatena_password
    consumer_key = settings.hatena_consumer_key
    consumer_secret = settings.hatena_consumer_secret
    # 取得したいアクセストークンのscope (カンマ区切り)
    scope = "read_public,read_private,write_public,write_private"
    print("Consumer Key: " + consumer_key)
    print("Consumer Secret: " + consumer_secret)

    request_token_and_secret = get_request_token(consumer_key, consumer_secret, scope)
    request_token = request_token_and_secret["request_token"]
    request_token_secret = request_token_and_secret["request_token_secret"]

    verifier = get_verifier_code(request_token, hatena_id, password)

    access_token_and_secret = get_access_token(consumer_secret, request_token, request_token_secret, verifier)
    access_token = access_token_and_secret["oauth_token"]
    access_secret = access_token_and_secret["oauth_token_secret"]
    print("Access Token: " + access_token)
    print("Access Token Secret: " + access_secret)
