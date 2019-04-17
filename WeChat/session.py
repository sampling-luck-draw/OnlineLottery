import time

SET_NICKNAME = 0
SET_AVATAR = 1
REMINDED_ALREADY = 3

class MySession:
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(MySession, cls).__new__(cls, *args, **kw)
        return cls._instance

    session = dict()

    def set(self, sid, content, expire=300):
        self.session[sid] = (content, time.time(), expire)

    def get(self, sid, default=None):
        if sid not in self.session:
            return default
        body = self.session[sid]
        if time.time() - body[1] > body[2]:
            del self.session[sid]
            return None
        return self.session[sid][0]

    def remove(self, sid):
        if sid in self.session:
            del self.session[sid]
