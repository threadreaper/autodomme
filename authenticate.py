import PySimpleGUI as sg
from options import OPTIONS
import sqlite3
import hashlib
import binascii
import os

conn = sqlite3.connect('teaseai.db')
c = conn.cursor()

def new_user(user: str, password: str):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    key = binascii.hexlify(key).decode()
    c.execute("INSERT INTO users VALUES (?, ?, ?)", (user, key, salt))
    conn.commit()
    c.close()
    conn.close()


def authenticate():
    username = OPTIONS['USERNAME']
    password = OPTIONS['PASSWORD']
    
    login_layout = [
        [sg.T('', size=(20,1), k='oops', visible=False)],
        [sg.T("Username:"), sg.Input(default_text=username, size=(20,1), k='USERNAME')],
        [sg.T("Password:"), sg.Input(default_text=password, size=(20,1), password_char='*', k='PASSWORD')],
        [sg.Checkbox('Save credentials', default=OPTIONS['SAVE_CREDENTIALS'], k='CREDENTIALS')],
        [sg.Submit(), sg.Cancel()]
    ]

    login = sg.Window("Please Authenticate", login_layout)

    while True:
        if len(OPTIONS['PASSWORD']) > 0:
            hash = False
        else:
            hash = True
        event, = login.read()
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            login.close()
            c.close()
            conn.close()
            return 1            
        elif event == 'Submit':
            username = login['USERNAME'].get()
            password = login['PASSWORD'].get()
            if hash:
                c.execute("SELECT salt FROM users WHERE username = ?", (username,))
                salt, = c.fetchone()            
                key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
                key = binascii.hexlify(key).decode()
            else:
                key = password       
            c.execute("SELECT username FROM users WHERE username = ? AND password = ?", (username, key))
            user = c.fetchone()[0]
            if login['CREDENTIALS'].get() == True:
                OPTIONS['USERNAME'] = username
                OPTIONS['PASSWORD'] = key
                OPTIONS['SAVE_CREDENTIALS'] = True
            if user:
                login.close()        
                return user
            else:
                login['oops'].update(text='Unable to authenticate', visible=True)
                login['USERNAME'].update("")
                login['PASSWORD'].update("")