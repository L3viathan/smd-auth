from __future__ import print_function
from flask import Flask, request, redirect, make_response
import random
import string

app = Flask(__name__)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Session(object):
    def __init__(self):
        self.session_id = id_generator()
        self.users = set()
        self.tokens = set()
        self.data = ""
        self.revision = 0
    def addUser(self):
        new_id = id_generator()
        self.users.add(new_id)
        return new_id
    def getSID(self):
        return self.session_id
    def generateToken(self):
        new_token = id_generator()
        self.tokens.add(new_token)
        return new_token
    def setData(self,data,revision):
        if self.revision == revision:
            self.data = data
            self.revision += 1
            return self.revision
        else:
            return False

sessions = dict()

@app.route('/')
def hello_world():
    return "Hello World, again!"

@app.route('/new')
def get_newSession():
    new_session = Session()
    new_user = new_session.addUser()
    new_sid = new_session.getSID()
    sessions[new_sid] = new_session
    app.logger.debug('Added session '+new_sid+' with user '+new_user)
    response = make_response(redirect('/session/' + new_sid))
    response.set_cookie(new_sid,new_user)
    return response
    # return "New User. ID:" + new_user + "\nSession ID:" + new_sid

@app.route('/session/<sid>')
def get_showSession(sid):
    username = request.cookies.get(sid)
    if sid in sessions and username in sessions.get(sid,None).users:
        return "authorized"
    else:
        return "unauthorized"

@app.route('/end/<sid>')
def delete_Session(sid):
    username = request.cookies.get(sid)
    if sid in sessions and username in sessions[sid].users:
        app.logger.debug('Removing user ' + username + ' from session ' + sid)
        sessions[sid].users.remove(username)
        if not sessions[sid].users:
            app.logger.debug('No users left, removing session ' + sid)
            del sessions[sid]
        response = make_response("ok")
        response.set_cookie(sid,'',expires=0) #remove cookie
        return response
    else:
        return "no", 401

@app.route('/generate/<sid>')
def get_token(sid):
    username = request.cookies.get(sid)
    if sid in sessions and username in sessions[sid].users:
        new_token = sessions[sid].generateToken()
        app.logger.debug('Generating token ' + new_token)
        return sid + "/" + new_token
    else:
        return "no"

@app.route('/enter/<sid>/<token>')
def join_session(sid, token):
    username = request.cookies.get(sid)
    if sid in sessions and username in sessions[sid].users:
        sessions[sid].tokens.remove(token)
        sessions[sid].users.remove(username)
        new_user = sessions[sid].addUser()
        response = make_response(redirect('/session/' + sid))
        response.set_cookie(sid,new_user)
        app.logger.debug('Revoking token ' + token + ', changing user ' + username + ' to ' + new_user + ' to session ' + sid)
        return response
    elif sid in sessions and token in sessions[sid].tokens:
        sessions[sid].tokens.remove(token)
        new_user = sessions[sid].addUser()
        response = make_response(redirect('/session/' + sid))
        response.set_cookie(sid,new_user)
        app.logger.debug('Revoking token ' + token + ', adding user ' + new_user + ' to session ' + sid)
        return response
    else:
        return "unauthorized"

@app.route('/pull/<sid>')
def get_data(sid):
    username = request.cookies.get(sid)
    if sid in sessions and username in sessions[sid].users:
        return (sessions[sid].data, sessions[sid].revision)
    else:
        return "unauthorized"

@app.route('/push/<sid>', methods = ['POST'])
def post_data(sid):
    username = request.cookies.get(sid)
    if sid in sessions and username in sessions[sid].users:
        new_revision = sessions[sid].setData(request.form['data'],request.form['revision'])
        if new_revision:
            return new_revision
        else:
            return "failed"

if __name__ == '__main__':
    app.debug = True #auto-reload on code changes
    app.run() # global: host='0.0.0.0')
