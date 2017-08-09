# -*- coding: utf-8 -*-

#
# Author: water - waterlzj@gmail.com
#
# Last modified: 2017-07-22 23:25 +0800
#
# Description: 
#

#!/usr/bin/env python
import os
from app import create_app
from app.models import User
from flask_script import Manager, Shell
from flask_admin import Admin

from gevent import pywsgi
from gevent import monkey; monkey.patch_all()



app = create_app(os.getenv('FLASK_CONFIG') or 'default')
admin = Admin(app, template_mode='bootstrap3')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, User=User)


manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
    #server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    #server.serve_forever()
