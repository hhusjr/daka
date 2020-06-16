import json
import re
import time
from collections import defaultdict

import requests
from requests import RequestException


def test_login(username, password):
    res = requests.post('http://ids.hhu.edu.cn/amserver/UI/Login', data={
        'Login.Token1': username,
        'Login.Token2': password,
    }, allow_redirects=False, timeout=(3, 5))
    return 'iPlanetDirectoryPro' in res.cookies


class DakaDFA:
    def __init__(self, username, password):
        self._session = None
        self._state_mapping = {
            0: ('登录', self._login, 3),
            1: ('获取问卷列表', self._get_form_list, 3),
            2: ('获取默认填表值', self._get_defaults, 3),
            3: ('打卡', self._daka, 3),

            4: ('用户名或密码错误', self._terminate, None),  # 用户名或密码错误
            5: ('操作成功', self._terminate, None),  # 操作成功
        }
        self._accept_states = {5}
        self._start_state = 0
        self._transition_table = [
            [0, 1, 4],
            [1, 2, 1],
            [2, 3, 2],
            [3, 5, 3],
            [None, None, None]
        ]
        self._username = username
        self._password = password
        self._fill_regex = re.compile(r'fillDetail\s=\s(\[.*?\]);')
        self._wid_regex = re.compile(r'_selfFormWid\s=\s\'(.*?)\';')
        self._form_info = {}

    def _terminate(self):
        return None

    def _login(self):
        self._session = requests.Session()
        self._session.max_redirects = 5
        res = self._session.post('http://ids.hhu.edu.cn/amserver/UI/Login', data={
            'Login.Token1': self._username,
            'Login.Token2': self._password,
        }, allow_redirects=False, timeout=(3, 5))
        # 用户名或密码错误
        if 'iPlanetDirectoryPro' not in res.cookies:
            return 2
        # 登陆成功
        return 1

    def _get_form_list(self):
        self._session.get('http://form.hhu.edu.cn/pdc/form/list', timeout=(3, 5))
        return 1

    def _get_defaults(self):
        res = self._session.get('http://form.hhu.edu.cn/pdc/formDesignApi/S/gUTwwojq', timeout=(3, 5))
        try:
            json_text = self._fill_regex.findall(res.text)[0]
            form_data = json.loads(json_text)
            wid = self._wid_regex.findall(res.text)[0]
            self._form_info = {
                'data': form_data[0],
                'wid': wid
            }
        except (json.JSONDecodeError, IndexError):
            return 0
        return 1

    def _daka(self):
        self._form_info['data']['DATETIME_CYCLE'] = time.strftime('%Y/%m/%d', time.localtime(time.time()))

        fields = {'DATETIME_CYCLE', 'XGH_336526', 'XM_1474', 'SFZJH_859173',
                  'SELECT_941320', 'SELECT_459666', 'SELECT_814855', 'SELECT_525884',
                  'SELECT_125597', 'TEXT_950231', 'TEXT_937296', 'RADIO_853789',
                  'RADIO_43840', 'RADIO_579935', 'RADIO_138407', 'RADIO_546905',
                  'RADIO_314799', 'RADIO_209256', 'RADIO_836972', 'RADIO_302717',
                  'RADIO_701131', 'RADIO_438985', 'RADIO_467360', 'PICKER_956186',
                  'TEXT_434598', 'TEXT_515297', 'TEXT_752063'}
        given_keys = list(self._form_info['data'].keys())
        for key in given_keys:
            if key not in fields:
                del self._form_info['data'][key]

        res = self._session.post('http://form.hhu.edu.cn/pdc/formDesignApi/dataFormSave', params={
            'wid': self._form_info['wid'],
            'userId': self._username
        }, data=self._form_info['data'], headers={
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'http://form.hhu.edu.cn',
            'Host': 'form.hhu.edu.cn',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }, timeout=(3, 5))
        try:
            return 1 if res.json()['result'] else 0
        except (KeyError, json.JSONDecodeError):
            return 0

    def run(self, callback=lambda x: None):
        current_state = self._start_state
        cnt = defaultdict(int)
        cnt[current_state] += 1
        while True:
            try:
                input_symbol = self._state_mapping[current_state][1]()
            except RequestException:
                input_symbol = 0
            if input_symbol is None:
                break
            if input_symbol >= len(self._transition_table[current_state]):
                return False, '非法输入'
            if self._transition_table[current_state][input_symbol] is None:
                break
            current_state = self._transition_table[current_state][input_symbol]
            cnt[current_state] += 1
            if self._state_mapping[current_state][2] is not None \
                    and cnt[current_state] > self._state_mapping[current_state][2]:
                callback('重试次数过多')
                return False, '重试次数过多'
            callback(self._state_mapping[current_state][0])
        return current_state in self._accept_states, self._state_mapping[current_state][0]
