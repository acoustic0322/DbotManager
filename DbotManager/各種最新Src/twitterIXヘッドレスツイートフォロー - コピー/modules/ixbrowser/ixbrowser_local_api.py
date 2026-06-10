import requests
import json
from loguru import logger

class Consts:
    ERROR_CODE_SUCCESS = 0
    ERROR_CODE_FAILURE = 1

class Profile:
    def __init__(self, profile_id=None, name=None, group_id=None):
        self.profile_id = profile_id
        self.name = name
        self.group_id = group_id
        self.site_url = "https://x.com"
        self.username = None
        self.password = None

import threading
import time

class IXBrowserClient:
    def __init__(self, target='127.0.0.1', port=53200):
        self.target = target
        self.port = port
        # Critical: Must include /api suffix
        self.base_url = f"http://{target}:{port}/api"
        self.timeout = 20
        self._local = threading.local()

    @property
    def code(self):
        if not hasattr(self._local, 'code'):
            self._local.code = 0
        return self._local.code

    @code.setter
    def code(self, value):
        self._local.code = value

    @property
    def message(self):
        if not hasattr(self._local, 'message'):
            self._local.message = ""
        return self._local.message

    @message.setter
    def message(self, value):
        self._local.message = value

    @property
    def data(self):
        if not hasattr(self._local, 'data'):
            self._local.data = None
        return self._local.data

    @data.setter
    def data(self, value):
        self._local.data = value

    @property
    def session(self):
        if not hasattr(self._local, 'session'):
            self._local.session = requests.Session()
        return self._local.session

    def _post(self, endpoint, payload):
        url = f"{self.base_url}{endpoint}"
        headers = {'Connection': 'close'}
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                resp = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    err_info = data.get('error', {})
                    self.code = err_info.get('code') if err_info else data.get('code', -1)
                    self.message = str(err_info.get('message', '')) or str(data.get('msg', ''))
                    self.data = data.get('data')
                    return data
                else:
                    self.code = -1
                    self.message = f"HTTP {resp.status_code}"
            except Exception as e:
                self.code = -1
                self.message = str(e)
                
            if attempt < max_retries - 1:
                logger.warning(f"API call to {endpoint} failed (Attempt {attempt+1}/{max_retries}): {self.message}. Retrying in 1s...")
                time.sleep(1.0)
                
        return {'error': {'code': self.code, 'message': self.message}}

    def get_profile_list(self, page=1, limit=100, keyword=None, group_id=None, offset=None):
        payload = {'page': page, 'limit': limit}
        if offset is not None: payload['page'] = (offset // limit) + 1
        if keyword:
            payload['keyword'] = keyword
            payload['title'] = keyword  # Some versions use title
            payload['q'] = keyword      # Some versions use q
        if group_id: payload['group_id'] = int(group_id)
        
        # Try both v2 and legacy
        res = self._post("/v2/profile-list", payload)
        if self.code != 0:
            res = self._post("/profile-list", payload)
        
        if self.code != 0:
            return None
            
        data = res.get('data', {})
        if data is None: return [] # Safety check
        if isinstance(data, list): return data
        return data.get('data') or data.get('list', [])

    def get_profile_detail(self, profile_id):
        payload = {'profile_id': int(profile_id)}
        res = self._post("/v2/profile-detail", payload)
        return res.get('data')

    def create_profile(self, profile_obj):
        payload = {'site_url': profile_obj.site_url, 'name': profile_obj.name}
        if profile_obj.username: payload['username'] = profile_obj.username
        if profile_obj.password: payload['password'] = profile_obj.password
        if profile_obj.group_id: payload['group_id'] = int(profile_obj.group_id)
        res = self._post("/v2/profile-create", payload)
        return res.get('data')

    def update_profile(self, profile_obj):
        payload = {
            'profile_id': int(profile_obj.profile_id),
            'name': profile_obj.name,
            'site_url': profile_obj.site_url
        }
        if profile_obj.group_id:
            payload['group_id'] = int(profile_obj.group_id)
        res = self._post("/v2/profile-update", payload)
        return res.get('data')

    def open_profile(self, profile_id, cookies_backup=True, load_profile_info_page=False, args=None):
        """
        Open profile with standard IXBrowser parameters.
        Must use Boolean types for backup/load.
        """
        payload = {
            'profile_id': int(profile_id),
            'cookies_backup': bool(cookies_backup),
            'load_profile_info_page': bool(load_profile_info_page)
        }
        if args:
            payload['args'] = args # Should be a list
            
        # Try prioritized endpoints
        for endpoint in ["/v2/profile-open", "/profile/open"]:
            res = self._post(endpoint, payload)
            
            if self.code == 0:
                return self.data
            
            if self.code == 111003:
                # Profile is already open — log the full response to check if address is embedded
                logger.warning(f"111003 raw response: code={self.code}, data={self.data}, res={res}")
                # Check multiple locations where the address might be
                if self.data and isinstance(self.data, dict) and 'debugging_address' in self.data:
                    logger.info(f"Profile {profile_id} already open — attaching to existing instance.")
                    return self.data
                # Some versions embed it directly in res
                if isinstance(res, dict) and isinstance(res.get('data'), dict) and 'debugging_address' in res.get('data', {}):
                    logger.info(f"Profile {profile_id} already open — attaching (from res.data).")
                    return res['data']
                # Address not found in response — break and let controller handle close+retry
                break
            
            # 1007 = endpoint not found, try fallback
            if self.code != 1007:
                break
                
        return None

    def close_profile(self, profile_id):
        payload = {'profile_id': int(profile_id)}
        self._post("/v2/profile-close", payload)
        if self.code != 0:
            self._post("/profile-close", payload)
        return self.code == 0
    
    def close_profiles_batch(self, profile_ids):
        """複数プロファイルを一括で閉じる"""
        payload = {'profile_id': [str(pid) for pid in profile_ids]}
        res = self._post("/v2/profile-close-in-batches", payload)
        return self.code == 0

    def get_group_list(self):
        all_groups = []
        page = 1
        limit = 100
        while True:
            res = self._post("/v2/group-list", {'page': page, 'limit': limit})
            if self.code != 0:
                break
            
            data = res.get('data', {})
            groups = data if isinstance(data, list) else data.get('data', [])
            
            if not groups:
                break
                
            all_groups.extend(groups)
            if len(groups) < limit:
                break
            page += 1
            
        return all_groups

    def get_profile_cookies(self, profile_id):
        res = self._post("/v2/profile-get-cookies", {'profile_id': int(profile_id)})
        if self.code == 0:
            c = res.get('data')
            if isinstance(c, str): return json.loads(c)
            return c
        return []

    def get_open_profiles(self):
        """Fetch list of currently running profiles with their debugging addresses."""
        # Correct endpoint found: /v2/profile-opened-list
        res = self._post("/v2/profile-opened-list", {})
        if self.code == 0:
            return self.data
        return []

    def reset_open_state(self, profile_id):
        """Reset 'Open' status in IX UI for ghost sessions."""
        payload = {'profile_id': int(profile_id)}
        res = self._post("/v2/profile-open-state-reset", payload)
        return self.code == 0

    # Aliases for reliability
    def get_profiles_list(self, *args, **kwargs):
        return self.get_profile_list(*args, **kwargs)
