#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from flask import Flask
from flask_weixin import Weixin

def hello():
    return 'Hello World!'

app = Flask(__name__)
app.secret_key = 'pikachu#robot'
app.config['WEIXIN_TOKEN'] = 'apuniangATnz'

weixin = Weixin(app)
app.add_url_rule('/', view_func=weixin.view_func)
app.add_url_rule('/hello', view_func=hello)



@weixin('*')
def reply_all(**kwargs):
    username = kwargs.get('sender')
    sender = kwargs.get('receiver')
    data = kwargs.get('content')
    message_type = kwargs.get('type')

    print kwargs
    
    content = 'res: %s ret:%s' % (data, time.time())

    return weixin.reply(
            username, sender=sender, content=content
        )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9999, debug=True)
