import sys
import tweepy
import secrets
import base64
import hashlib
import os
import re

import tweepy
#print(tweepy.__version__)

import oauthlib
#print(oauthlib.__version__)

import requests_oauthlib
#print(requests_oauthlib.__version__)

def generate_code_verifier():
    code_verifier = secrets.token_urlsafe(64)
    return code_verifier

def generate_code_challenge(code_verifier):
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).rstrip(b'=').decode('utf-8')
    return code_challenge

def generate_auth_url(client_id, client_secret):
    scopes = [
        "tweet.read",
        "tweet.write",
        "users.read",
        "offline.access",
        "bookmark.read",
        "bookmark.write"
    ]

    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

#    print(code_verifier)
#    print(code_challenge)

    # 任意の文字列とその変換形を作成
    code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")

    auth = tweepy.OAuth2UserHandler(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri='https://script.google.com/macros/s/AKfycbzVkmUti3NUc5T1MxSfX586zn8Iv4i1l-fMSlMb99gIl5Wlius5Sf-CkQP4zenPlpl_AQ/exec',
        scope=scopes,
#        code_challenge=code_challenge,
#        code_challenge_method="S256"  # 必須
    )

    return auth.get_authorization_url()
#    return auth.get_authorization_url(code_challenge=code_challenge, code_challenge_method="S256")

if __name__ == "__main__":
    client_id = sys.argv[1]
    client_secret = sys.argv[2]
    auth_url = generate_auth_url(client_id, client_secret)
    print(auth_url)
