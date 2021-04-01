import argparse
from base64 import b64encode
from pathlib import Path
import tkinter as tk

from smtp_client.client import Client
from smtp_client.const import LOGIN_WINDOW_SIZE
from smtp_client.message import Message


def arg_parser():
    parser = argparse.ArgumentParser(description=
                                     'SMTP-MIME - Sends all files '
                                     'from the catalog to the recipient')
    parser.add_argument('--ssl', nargs=1, type=bool,
                        help='Allow the use of ssl', default=False)
    parser.add_argument('-s', '--server', type=str, nargs=1,
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
    parser.add_argument('--auth ', type=bool,
                        help='whether to request authorization '
                             '(by default, no)', default=False)
    parser.add_argument('-v', '--verbose', type=bool,
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
    x_coord = (screen_width / 2) - (LOGIN_WINDOW_SIZE[0] / 2)
    y_coord = (screen_height / 2) - (LOGIN_WINDOW_SIZE[1] / 2)
    gui.geometry('%dx%d+%d+%d' % (LOGIN_WINDOW_SIZE[0], LOGIN_WINDOW_SIZE[1], x_coord, y_coord))
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

    return b64encode(email.get()), b64encode(password.get())


def get_files(path: Path):
    def get_text(file):
        temp = ''
        for j in file:
            temp += j
        return temp

    if path.is_dir():
        for i in path.iterdir():
            if i.is_file():
                yield i.name, get_text(i.open())


args = arg_parser().parse_args()
login, password = b'', b''
if args.auth:
    login, password = login_gui()
client = Client(args.ssl, args.server, args.toe, args.frome,
                args.verbose, login, password)
msg = Message(args.frome, args.toe, args.subject)
remaining_size = client.get_max_size() - msg.get_size(msg)
fl = False
for file in get_files(args.directory):
    if remaining_size - msg.get_size(file[1]) <= 0:
        fl = True
        client.send_mail(msg)
        msg = Message(args.frome, args.toe, args.subject)
        remaining_size = client.get_max_size() - msg.get_size(msg)
    else:
        fl = False
        msg.add_part(*file)

if fl:
    client.send_mail(msg)
