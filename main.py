#!/usr/bin/env python

import os, tornado, json, random
from tornado import websocket
from housepy import config, log, tornado_server, process, jobs, strings

process.secure_pid(os.path.join(os.path.dirname(__file__), "run"))

class Controller(tornado_server.Handler):

    def get(self, page=None):
        return self.render("blank.html")


class WebSocket(websocket.WebSocketHandler):

    users = {}
    sockets = {}

    def open(self):
        log.info("//////////// WebSocket.open")
        user_id = strings.random_string(10)
        WebSocket.sockets[user_id] = self
        log.info("--> user_id %s" % user_id)
        available_users = [uid for uid in WebSocket.users.keys() if WebSocket.users[uid] is None]
        log.debug("--> available users: %s" % available_users)
        if len(available_users):
            partner_id = random.choice(available_users)
            WebSocket.users[partner_id] = user_id
            WebSocket.users[user_id] = partner_id
            log.debug("--> linked with %s" % partner_id)
        else:
            WebSocket.users[user_id] = None
        log.debug("--> users %s" % WebSocket.users)
        self.send(user_id)

    def on_message(self, data):
        log.info("//////////// WebSocket.on_message %s" % data)
        try:
            data = json.loads(data)
            url = data['url']
            user_id = data['user_id']
        except Exception as e:
            log.error(log.exc(e))
            return
        log.info("--> user_id %s" % user_id)            
        if user_id not in WebSocket.users:
            log.warning("--> %s (originator) not in WebSocket.users" % user_id)
            return
        receiver_id = WebSocket.users[user_id]
        if receiver_id is None:
            log.info("--> no receiver")
            return
        if receiver_id not in WebSocket.sockets:
            log.warning("--> %s (receiver) not in WebSocket.users" % receiver_id)
            return
        WebSocket.sockets[receiver_id].send(url)
        self.send("OK")

    def on_close(self):
        log.info("//////////// WebSocket.on_close")
        user_id = None
        for uid, instance in WebSocket.sockets.items():
            if instance == self:
                user_id = uid
        log.info("--> user_id %s" % user_id)                
        if user_id is None:
            log.warning("socket for %s not found" % user_id)
            return
        if user_id in WebSocket.users:
            del WebSocket.users[user_id]
        for uid, partner_id in WebSocket.users.items():
            if partner_id == user_id:
                WebSocket.users[uid] = None        
        log.info("--> complete")

    def send(self, message):
        log.info("--> sending [%s]" % message)
        self.write_message(message)

def main():
    handlers = [
        (r"/websocket", WebSocket),    
        (r"/?([^/]*)", Controller),
    ]
    tornado_server.start(handlers)      
                     
if __name__ == "__main__":
    main()

