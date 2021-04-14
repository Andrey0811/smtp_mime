# -*- coding: utf-8 -*-

from pathlib import Path

from smtp_client.const import LINE_BREAK, SEPARATE_DEFAULT
from smtp_client.message import Message
from smtp_client.utils import get_size, get_files


def test_message():
    from_em = 'test@mail.ru'
    to_em = 'test2@mail.ru'
    msg = Message(from_em, to_em, 'test')
    msg_size = get_size(msg)
    path = Path('C:\\Study\\протоколы интернет\\дз\\smtp-mime\\tests\\resources')
    for name, item in get_files(path):
        size = get_size(item)
        assert size == 50
        msg.add_part(name, item)
        assert msg_size < get_size(msg)

    msg_str = str(msg)
    assert msg_str.lower().startswith(f'from: <{from_em}>{LINE_BREAK}to: <{to_em}>{LINE_BREAK}')
    assert msg_str.lower().endswith(f'--{SEPARATE_DEFAULT}--{LINE_BREAK}')
