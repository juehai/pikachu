#!/usr/bin/env python
# -*- coding: utf-8 -*-

import views
from config import config
from flask import Flask


app = Flask(__name__)
app_config = config.get('HTTP', None)

# flask URL routing
app.add_url_rule('/', view_func=views.hello)
app.add_url_rule('/wechat', view_func=views.wechat, methods=['GET', 'POST'])
app.add_url_rule('/hello', view_func=views.hello)

app.secret_key = app_config['secret_key']

if __name__ == '__main__':

    app.run(host=app_config['host'], 
            port=app_config['port'], 
            debug=app_config['debug'])
