from __future__ import print_function
from flask import Flask, request, redirect, make_response, jsonify
import random
import string
import json
from flasktools import crossdomain

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
        if self.revision == int(revision):
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
@crossdomain(origin='*')
def get_newSession():
    new_session = Session()
    new_user = new_session.addUser()
    new_sid = new_session.getSID()
    sessions[new_sid] = new_session
    app.logger.debug('Added session '+new_sid+' with user '+new_user)
    # response = make_response(redirect('/session/' + new_sid))
    return jsonify(sid=new_sid, uid=new_user, status="ok")
    # return "New User. ID:" + new_user + "\nSession ID:" + new_sid

@app.route('/end', methods=['GET'])
@crossdomain(origin='*')
def delete_Session():
    username = request.args['uid']
    sid = request.args['sid']
    if sid in sessions and username in sessions[sid].users:
        app.logger.debug('Removing user ' + username + ' from session ' + sid)
        sessions[sid].users.remove(username)
        if not sessions[sid].users:
            app.logger.debug('No users left, removing session ' + sid)
            del sessions[sid]
        return jsonify(status="ok")
    else:
        return jsonify(status="fail")

@app.route('/generate', methods=['GET'])
@crossdomain(origin='*')
def get_token():
    sid = request.args['sid']
    username = request.args['uid']
    if sid in sessions and username in sessions[sid].users:
        new_token = sessions[sid].generateToken()
        app.logger.debug('Generating token ' + new_token)
        return jsonify(sid=sid, token=new_token, status="ok")
    else:
        return jsonify(status="fail")

@app.route('/enter', methods = ['GET'])
@crossdomain(origin='*')
def join_session():
    sid = request.args['sid']
    token = request.args['token']
    if sid in sessions and token in sessions[sid].tokens:
        sessions[sid].tokens.remove(token)
        new_user = sessions[sid].addUser()
        app.logger.debug('Revoking token ' + token + ', adding user ' + new_user + ' to session ' + sid)
        return jsonify(sid=sid, uid=new_user, status="ok")
    else:
        return jsonify(status="fail")

@app.route('/pull', methods = ['GET'])
@crossdomain(origin='*')
def get_data():
    sid = request.args['sid']
    username = request.args['uid']
    if sid in sessions and username in sessions[sid].users:
        return jsonify(data=sessions[sid].data, revision=sessions[sid].revision, status="ok")
    else:
        return jsonify(status="fail")

@app.route('/push', methods = ['GET'])
@crossdomain(origin='*')
def post_data():
    sid = request.args['sid']
    username = request.args['uid']
    if sid in sessions and username in sessions[sid].users:
        thedata = request.args.get('data','')
        new_revision = sessions[sid].setData(thedata,request.args['revision'])
        if new_revision:
            return jsonify(revision=new_revision, status="ok")
        else:
            print("failing, revision is",new_revision)
            return jsonify(status="fail")

if __name__ == '__main__':
    app.debug = True #auto-reload on code changes
    app.run() # global: host='0.0.0.0')
