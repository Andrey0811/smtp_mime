# -*- coding: utf-8 -*-

import argparse
from base64 import b64encode
from pathlib import Path
import tkinter as tk

import smtp_client.client
import smtp_client.const
from smtp_client.message import Message
from smtp_client.utils import get_files, get_size


def arg_parser():
    parser = argparse.ArgumentParser(description=
                                     'SMTP-MIME - Sends all files '
                                     'from the catalog to the recipient')
    parser.add_argument('--ssl', action='store_true',
                        help='Allow the use of ssl', default=False)
    parser.add_argument('-s', '--server', type=str,
                        help='Address (or domain name) of SMTP server '
                             'in the format address [:port] (default port 25)')
    parser.add_argument('-t', '--toe', type=str, nargs=1,
                        help='recipient`s email address')
    parser.add_argument('-f', '--frome', type=str,
                        help='sender`s postal address', default='')
    parser.add_argument('--subject', type=str,
                        help='email subject, the default '
                             'subject is "Happy Pictures"',
                        default='Happy Pictures')
    parser.add_argument('--auth', action='store_true',
                        help='whether to request authorization '
                             '(by default, no)', default=False)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='displaying the work log', default=False)
    parser.add_argument('-d', '--directory', type=str,
                        help='directory with images (default $pwd)',
                        default=Path.cwd())
    return parser


def login_gui():
    gui = tk.Tk()
    gui.title('ESMTP Client')
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    x_coord = (screen_width / 2) - (smtp_client.const.LOGIN_WINDOW_SIZE[0] / 2)
    y_coord = (screen_height / 2) - (smtp_client.const.LOGIN_WINDOW_SIZE[1] / 2)
    gui.geometry('%dx%d+%d+%d' % (smtp_client.const.LOGIN_WINDOW_SIZE[0], smtp_client.const.LOGIN_WINDOW_SIZE[1], x_coord, y_coord))
    tk.Label(gui, text='Email Address:').grid(row=1)
    tk.Label(gui, text='Password:       ').grid(row=2)

    email = tk.StringVar()
    email_input = tk.Entry(gui, textvariable=email)
    email_input.grid(row=1, column=1)

    password = tk.StringVar()
    password_input = tk.Entry(gui, textvariable=password, show='*')
    password_input.grid(row=2, column=1)

    auth_button = tk.Button(gui, text='Auth', width=25, command=gui.destroy)
    auth_button.grid(row=3, column=1)

    gui.mainloop()
    return b64encode(email.get().encode()), b64encode(password.get().encode())


def main():
    args = arg_parser().parse_args()
    login, password = b'', b''
    if args.auth:
        login, password = login_gui()
    client = smtp_client.client.Client(args.ssl, args.server, args.toe[0], args.frome,
                    args.verbose, login, password)
    msg = Message(args.frome, args.toe[0], args.subject)
    remaining_size = client.get_max_size() - get_size(msg)
    client.ehlo()
    client.hello_recv()
    if not args.ssl:
        client.start_tls()
        client.hello_recv()
    client.auth()
    for file in get_files(Path(args.directory)):
        if remaining_size - get_size(file[1]) <= 0:
            client.send_mail(msg)
            msg = Message(args.frome, args.toe, args.subject)
            remaining_size = client.get_max_size() - get_size(msg)
        else:
            msg.add_part(*file)
    client.send_mail(msg)


if __name__ == '__main__':
    main()
