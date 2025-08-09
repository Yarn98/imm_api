#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Offline demo to learn the EMI/HMI call flow without any hardware.
It simulates connect/login/get_param/logout/close using the same surface API
as `imm.EMI_Interface`.
"""

import datetime
from typing import Dict, List, Union

from imm import EMI_Interface


class FakeEMI(EMI_Interface):
    """
    A lightweight EMI simulator for offline learning. It mimics a subset of the
    EMI_Interface public API without opening any sockets.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_connected = False
        self._is_logged_in = False
        # Provide a tiny in-memory parameter store for demo purposes
        self._param_store: Dict[str, Union[str, float, int]] = {
            # Example URIs
            'cc300://imm/cm#//c.ShotCounter/p.sv_iShotCounter/v': 12345,
            'cc300://imm/cm#//c.PDP/p.sv_dPDPDate/v': '2025-01-01T00:00:00',
            'cc300://imm/cm#//c.PDP/p.sv_dPDPTime/v': '2025-01-01T00:00:00',
        }

    # --- Lifecycle methods (no-ops offline) ---
    def connect(self) -> bool:
        print('[offline] connect() -> success (simulated)')
        self._is_connected = True
        return True

    def login(self) -> None:
        if not self._is_connected:
            print('[offline] login() called before connect(); continuing in offline mode')
        self._is_logged_in = True
        print('[offline] login() -> ok (simulated)')

    def logout(self) -> None:
        self._is_logged_in = False
        print('[offline] logout() -> ok (simulated)')

    def close(self) -> None:
        self._is_connected = False
        print('[offline] close() -> ok (simulated)')

    # --- Data methods (return synthetic values) ---
    def get_param_value(self, param_uri: Union[str, List[str]]):
        if isinstance(param_uri, str):
            param_list = [param_uri]
        else:
            param_list = list(param_uri)

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        result: Dict[str, Union[str, float, int]] = {}
        for uri in param_list:
            result[uri] = self._param_store.get(uri, 'N/A')
        # Provide a timestamp similar to the real interface
        result['timestamp_EMI'] = now
        return result

    def set_param_value(self, param_uri: str, value):
        self._param_store[param_uri] = value
        print(f"[offline] set_param_value(uri={param_uri}, value={value}) -> ok")
        return True


if __name__ == '__main__':
    # Parameters settings (kept for parity with the online example; values are unused offline)
    NAME = 'EMI'
    IP = '127.0.0.1'
    PORT = 10050
    USERNAME = 'user'
    PASSW = 'pass'
    uri_shotcounter = 'cc300://imm/cm#//c.ShotCounter/p.sv_iShotCounter/v'

    # Create the offline EMI instance
    e = FakeEMI(name=NAME, ip=IP, port=PORT, username=USERNAME, passw=PASSW, debug=True)

    # Typical flow: connect -> login -> get param -> set param -> get again -> logout -> close
    e.connect()
    e.login()

    print('\n[offline] Reading parameter once:')
    param = e.get_param_value(uri_shotcounter)
    print('Get Shot Counter :', param[uri_shotcounter], '| timestamp:', param['timestamp_EMI'])

    print('\n[offline] Setting parameter (simulated):')
    e.set_param_value(uri_shotcounter, 12346)
    param = e.get_param_value(uri_shotcounter)
    print('Get Shot Counter :', param[uri_shotcounter], '| timestamp:', param['timestamp_EMI'])

    e.logout()
    e.close()