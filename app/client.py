
import requests
from base64 import b64encode
from collections import namedtuple

from app.models import ApiKey, UserProfile


class LiveCodingClient:

    host = "https://www.livecoding.tv/api"
    version = "/v1"

    def __init__(self, livetvusername):
        self.livetvusername = livetvusername
        self.access = UserProfile.objects.get(livetvusername=livetvusername)
        self.key = ApiKey.objects.get(provider="livecodingtv")
        self.headers = self._build_headers(self.access.oauth_token)

    @staticmethod
    def _build_headers(token):
        return {
            'authorization': "Bearer {}".format(token),
            'cache-control': "no-cache",
        }

    @staticmethod
    def get_redirect_url():
        api_key = ApiKey.objects.get(provider="livecodingtv")
        base_redirect_url = "https://www.livecoding.tv/o/authorize/?scope=read&state={}&redirect_uri={}&response_type=code&client_id={}"
        return base_redirect_url.format(api_key.state, api_key.redirect_url, api_key.client_id)

    def _data_factory(self, name, data):
        return namedtuple(name, data.keys())(**data)

    def _make_request(self, url):
        request_url = "{}{}{}".format(self.host, self.version, url)
        response = requests.get(request_url, headers=self.headers)
        # if 401 (auth not provided, lets get a new token and retry?)
        if response.status_code == 401:
            self.access = LiveCodingAuthClient(
                code=self.access.oauth_access_code, refresh=True).get_auth_token(self.access.user)[0]
            headers = self._build_headers(self.access)
            response = requests.get(request_url, headers=headers)
        self.key.increment()
        return response.json()

    @classmethod
    def get_user_from_token(cls, token):
        headers = cls._build_headers(token)
        data = requests.get("{}/v1/user/".format(cls.host), headers=headers).json()
        return namedtuple("user", data.keys())(**data)

    def get_user_details(self):
        user_details = self._make_request("/user/")
        return self._data_factory("user", user_details)

    def get_stream_details(self):
        # No permission with only 'read' scope
        stream_details = requests.get(
            "{}/v1/livestreams/{}/".format(self.host, self.livetvusername), headers=self.headers).json()
        return self._data_factory("stream", stream_details)

    def get_onair_streams(self):
        stream_details = self._make_request("/livestreams/onair/")
        return self._data_factory("stream", stream_details)

    def _get_paginated_data(self, data_class, url, stream_details):
        get_data = lambda self, stream_details: [self._data_factory(data_class, obj) for obj in stream_details["results"]]
        yield get_data(self, stream_details)
        while stream_details["next"]:
            next_params = stream_details["next"][stream_details["next"].index("?"):]
            stream_details = self._make_request("{}{}".format(url, next_params))
            yield get_data(self, stream_details)

    def get_user_videos(self):
        return self.get_videos(url="/user/videos/")

    # TODO: testme
    def get_videos(self, url="/videos/"):
        stream_details = self._make_request(url)
        if not stream_details["next"]:
            return [[self._data_factory("video", video) for video in stream_details["results"]]]

        return self._get_paginated_data("video", url, stream_details)


class LiveCodingAuthClient:

    auth_url = "https://www.livecoding.tv/o/token/"
    payload_body = "code={}&grant_type={}&redirect_uri={}&client_id={}&client_secret={}"

    def __init__(self, code, refresh=False):
        self.refresh = refresh
        self.code = code
        self.key = ApiKey.objects.get(provider="livecodingtv")
        self.basic_auth_header_val = b64encode(str.encode("{}:{}".format(self.key.client_id, self.key.client_secret)))
        self.payload = self.payload_body.format(
            code,
            "authorization_code",
            self.key.redirect_url,
            self.key.client_id,
            self.key.client_secret
        )
        self.headers = {
            'authorization': "Basic " + self.basic_auth_header_val.decode("utf-8"),
            'cache-control': "no-cache",
            'content-type': "application/x-www-form-urlencoded"
        }

    def get_auth_token(self, user):
        payload = self.payload
        if self.refresh:
            refresh_token = user.userprofile.oauth_refresh_token
            payload_body = "grant_type={}&redirect_uri={}&client_id={}&client_secret={}"
            payload = payload_body.format(
                "refresh_token",
                self.key.redirect_url,
                self.key.client_id,
                self.key.client_secret
            ) + "&refresh_token={}".format(refresh_token)
            response = requests.post(self.auth_url, data=payload, headers=self.headers).json()
            user.userprofile.oauth_token = response['access_token']
            user.userprofile.oauth_refresh_token = response['refresh_token']
            user.userprofile.save()
            return response['access_token'], response["refresh_token"]
        response = requests.post(self.auth_url, data=payload, headers=self.headers).json()
        return response['access_token'], response["refresh_token"]
