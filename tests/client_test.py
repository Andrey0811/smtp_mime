# -*- coding: utf-8 -*-

from smtp_client.client import Client
from smtp_client.message import Message


def test_client_one():
    cl = Client(False, 'smtp.yandex.ru:25',
                'andreyozhigoff@yandex.ru', '0811andrey0811@mail.ru',
                True, bytes('YW5kcmV5b3poaWdvZmZAeWFuZGV4LnJ1', encoding='utf-8'),
                bytes('VXJmQWpidkV4b3FOMDgxMQ==', encoding='utf-8'))
    cl.ehlo()
    cl.start_tls()
    cl.ehlo()
    cl.auth()
    msg = Message('andreyozhigoff@yandex.ru',
                  '0811andrey0811@mail.ru', 'Hello')
    msg.add_part('resources/body.html', '''<!DOCTYPE HTML "Name">
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=ITF-8">
  </head>
  <body bgcolor="#ffffff" text="#000567">
	<center style="width: 100%;table-layout: fixed;">
	<div style="max-width: 320px;">
		<img src="cid:part2.1.1" alt="" style="width: 50%;height: 20%;" />
		<h1>RFC2047</h1>
		Описывает разметку .EML письма.
	</div>
  </body>
 </html>''')
    cl.send_mail(msg)


# todo change login and password in base64 for test
def test_client_two():
    cl = Client(True, 'smtp.yandex.ru:465',
                'from@mail.ru', 'to@mail.ru',
                True, bytes('login', encoding='utf-8'),
                bytes('password', encoding='utf-8'))
    cl.ehlo()
    cl.auth()
    msg = Message('andreyozhigoff@yandex.ru',
                  '0811andrey0811@mail.ru', 'Hello')
    msg.add_part('resources/body.html', '''<!DOCTYPE HTML "Name">
    <html>
      <head>
        <meta http-equiv="content-type" content="text/html; charset=ITF-8">
      </head>
      <body bgcolor="#ffffff" text="#000567">
    	<center style="width: 100%;table-layout: fixed;">
    	<div style="max-width: 320px;">
    		<img src="cid:part2.1.1" alt="" style="width: 50%;height: 20%;" />
    		<h1>RFC2047</h1>
    		Описывает разметку .EML письма.
    	</div>
      </body>
     </html>''')
    cl.send_mail(msg)
