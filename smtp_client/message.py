# -*- coding: utf-8 -*-

import locale
from collections import OrderedDict
from datetime import datetime
import magic
from dateutil.tz import tzlocal
from base64 import b64encode

from smtp_client.const import SEPARATE_DEFAULT, LINE_BREAK, ENCODING_DEFAULT


class Message:
    def __init__(self, from_email: str, to_email: str, subject: str):
        self._headers = OrderedDict({'From': f'<{from_email}>',
                        'To': f'<{to_email}>',
                        'Return-Path': f'<{from_email}>',
                        'Return-Receipt-To': f'<{from_email}>',
                        # 'Date': self.get_date(),
                        'Subject': subject,
                        'Content-Type': f'multipart/mixed; '
                                        f'boundary = {SEPARATE_DEFAULT}'})
        self._parts = []

    # @staticmethod
    # def get_date(format_time='%a, %d %b %Y %H:%M:%S %z'):
    #     return datetime.now(locale.getlocale()).strftime(format_time)

    def add_part(self, name_part: str, code_part: str): # в name_part класть относительный или аосолютный путь
        idx = len(self._parts) + 1
        header = OrderedDict({'Content-Type': f'{magic.from_file(name_part, mime=True)};',
                  'Content-Transfer-Encoding': 'base64',
                  'Content-Id': f'<part{idx}.{idx}.{idx}>',
                  'Content-Disposition': f'attachment; filename={name_part};',
                  'Content': b64encode(bytes(code_part, encoding=ENCODING_DEFAULT))})
        self._parts.append(header)

    def __repr__(self):
        temp = ''
        for header in self._headers.keys():
            temp += f'{header}: {self._headers.get(header)}{LINE_BREAK}'
        temp += LINE_BREAK

        for part in self._parts:
            temp += f'--{SEPARATE_DEFAULT}{LINE_BREAK}'
            for header in part.keys():
                if header != 'Content':
                    temp += f'{header}: {part.get(header)}{LINE_BREAK}'
            temp += LINE_BREAK
            temp += str(part.get('Content'))

        temp += f'--{SEPARATE_DEFAULT}--{LINE_BREAK}'
        return temp
