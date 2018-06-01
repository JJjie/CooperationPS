# -*- coding: utf-8 -*-
# @Time    : 2018/5/31 13:54
# @Author  : UNE
# @Project : cps-server
# @File    : app.py
# @Software: PyCharm

async_mode = 'eventlet'

import random
from pathlib import Path
import base64
import time
import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, render_template, request, jsonify, send_from_directory
import imageProcessing as facep

sio = socketio.Server(logger=True, async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
app.config['SECRET_KEY'] = 'secret!'

UPLOAD_FOLDER = 'upload'
basedir = Path(__file__).parent.absolute()
file_dir = basedir / UPLOAD_FOLDER
file_dir.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = set(['png','jpg','JPG','PNG','gif','GIF'])

# cache
class RoomInfo:
    def __init__(self):
        self.roomid = 0000
        self.users = []
        self.position = {}
        self.select = {}
roomDB = {}
roomContainer = []

def getRoomID():
    while True:
        id = random.random() * 10000
        if id not in roomContainer:
            roomContainer.append(id)
            return id

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

# -----------------------------------------------------------
# route
@app.route('/')
def index():
    return render_template('index.html')


# upload the image
@app.route('/imgfile/upload', methods=['POST'], strict_slashes=False)
def img_upload():
    f = request.files['imgfile']
    if f and allowed_file(f.filename):
        ext = f.filename.rsplit('.', 1)[1]
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.' + ext
        f.save(file_dir / new_filename)
        token = base64.b64encode(new_filename)
        return jsonify({"errno": 0, "errmsg": "success", "img_token": token})
    else:
        return jsonify({"errno": 1, "errmsg": "fail"})

# get the image
@app.route('/imgfile/show/<token>')
def get_fig(token):
    filename = base64.b64decode(token)
    file_path = file_dir / filename
    if file_path.is_file():
        return send_from_directory(file_dir, filename, as_attachment=True)



# -----------------------------------------------------------
# socketio

@sio.on('my event', namespace='/cps')
def message(sid, message):
    sio.emit('my response', {'data': message['data']}, room=sid, namespace='/cps')

@sio.on('disconnect request', namespace='/cps')
def disconnect_request(sid):
    sio.disconnect(sid, namespace='/cps')


@sio.on('connect', namespace='/cps')
def connect(sid, message):
    sio.emit('my response', {'data': 'Connected', 'count': 0}, room=sid,
             namespace='/cps')


@sio.on('disconnect', namespace='/cps')
def disconnect(sid):
    print('Client disconnected')

# Room
@sio.on('createRoom', namespace='/cps')
def create(sid, message):
    roomid = getRoomID()
    userid = message['userid']
    roomDB[roomid] = RoomInfo()
    roomDB[roomid].roomid = roomid
    roomDB[roomid].users.append(userid)
    sio.enter_room(sid, roomid, namespace='/cps')
    sio.emit('my response', {'userid': userid,
                             'roomid': roomid,
                             'errno': 0,
                             'errmsg': 'success'},
             room=sid, namespace='/cps')

# join a room
@sio.on('joinRoom', namespace='/cps')
def join(sid, message):
    roomid = message['roomid']
    userid = message['userid']
    roomDB[roomid].users.append(userid)
    sio.enter_room(sid, roomid, namespace='/cps')
    sio.emit('my response', {'users': roomDB[roomid].users,
                             'roomid': roomid,
                             'errno': 0,
                             'errmsg': 'success'},
             room=roomid, namespace='/cps')

# leave the room
@sio.on('leaveRoom', namespace='/cps')
def leave(sid, message):
    roomid = message['roomid']
    userid = message['userid']
    roomDB[roomid].users.pop(roomDB[roomid].users.index(userid))
    sio.leave_room(sid, message['room'], namespace='/cps')
    sio.emit('my response', {'users': roomDB[roomid].users,
                             'roomid': roomid,
                             'errno': 0,
                             'errmsg': 'success'},
             room=roomid, namespace='/cps')

# close the room
@sio.on('closeRoom', namespace='/cps')
def close(sid, message):
    roomid = message['roomid']
    del roomDB[roomid]
    sio.emit('my response', {'errno': 0, 'errmsg': 'success'}, roomid, namespace='/cps')
    sio.close_room(roomid, namespace='/cps')

# ------------------------------------------------------------
# face recognition
@sio.on('showface', namespace='/cps')
def showface(sid, message):
    token = message['img_token']
    roomid = message['roomid']
    filename = base64.b64decode(token)
    file_path = file_dir / filename
    position = facep.recognizeFace(file_path)
    for i in range(len(position)):
        roomDB[roomid].position[i] = position[i]
    sio.emit('my response', {'position': roomDB[roomid].position,
                             'img_token': token,
                             'errno': 0,
                             'errmsg': 'success'},
             room=roomid, namespace='/cps')

# add face without recognition
@sio.on('addface', namespace='/cps')
def addface(sid, message):
    roomid = message['roomid']
    position = message['position']

    index = max(roomDB[roomid].position.keys()) + 1
    roomDB[roomid].position[index] = position
    sio.emit('my response', {'position': roomDB[roomid].position,
                             'errno': 0,
                             'errmsg': 'success'},
             room=roomid, namespace='/cps')

# delete the error face
@sio.on('deleteface', namespace='/cps')
def deleteface(sid, message):
    roomid = message['roomid']
    positionid = message['positionid']
    del roomDB[roomid].position[positionid]
    sio.emit('my response', {'position': roomDB[roomid].position,
                             'errno': 0,
                             'errmsg': 'success'},
             room=roomid, namespace='/cps')

# get the current occupation
@sio.on('occupation', namespace='/cps')
def getOccupation(sid, message):
    roomid = message['roomid']
    sio.emit('my response', {'occupation': roomDB[roomid].select,
                             'errno': 0,
                             'errmsg': 'success'},
             room=roomid, namespace='/cps')

# select your face
@sio.on('selectface', namespace='/cps')
def selectface(sid, message):
    faceid = message['faceid']
    userid = message['userid']
    roomid = message['roomid']

    if faceid in roomDB[roomid].select.values():
        sio.emit('my response', {'errno': 2,
                                 'errmsg': 'occupied'},
                 room=sid, namespace='/cps')
    elif userid in roomDB[roomid].select.keys():
        sio.emit('my response', {'errno': 3,
                                 'errmsg': 'selected'},
                 room=sid, namespace='/cps')
    else:
        roomDB[roomid].select[userid] = faceid
        sio.emit('my response', {'occupation': roomDB[roomid].select,
                                 'errno': 0,
                                 'errmsg': 'success'},
                 room=roomid, namespace='/cps')

# cancel your selection
@sio.on('facecancel', namespace='/cps')
def facecancel(sid, message):
    userid = message['userid']
    roomid = message['roomid']

    del roomDB[roomid].select[userid]
    sio.emit('my response', {'occupation': roomDB[roomid].select,
                             'errno': 0,
                             'errmsg': 'success'},
             room=roomid, namespace='/cps')

# save the position after modification
@sio.on('savefacePos', namespace='/cps')
def savefacePos(sid, message):
    roomid = message['roomid']
    userid = message['userid']
    position = message['position']
    roomDB[roomid].position[roomDB[roomid].select[userid]] = position
    sio.emit('my response', {'errno': 0, 'errmsg': 'success'}, room=sid, namespace='/cps')


# upload the image after modification
@sio.on('uploadPSface', namespace='/cps')
def uploadPSface(sid, message):
    roomid = message['roomid']
    userid = message['userid']
    token = message['img_token']
    originfilename = base64.b64decode(token)
    position = roomDB[roomid].position[roomDB[roomid].select[userid]]

    f = request.files['imgfile']
    if f and allowed_file(f.filename):
        ext = f.filename.rsplit('.', 1)[1]
        unix_time = int(time.time())
        new_filename = str(roomid) + "_" + str(userid) + "_" + str(unix_time) + '.' + ext
        f.save(file_dir / new_filename)
        facep.mergeImage(position, file_dir, new_filename, originfilename)
        sio.emit('my response', {'errno': 0,
                                 'errmsg': 'success',
                                 'img_token': token}, room=roomid, namespace='/cps')
    else:
        sio.emit('my response', {'errno': 1, 'errmsg': 'fail'}, room=sid, namespace='/cps')


# finish the cooperation and return the fig
@sio.on('finishPS', namespace='/cps')
def finishPS(sid, message):
    roomid = message['roomid']
    token = message['img_token']
    sio.emit('my response', {'errno': 0,
                             'errmsg': 'success',
                             'finishflag': 1,
                             'img_token': token},
             room=roomid, namespace='/cps')


if __name__ == '__main__':
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)