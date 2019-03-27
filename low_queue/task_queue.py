import os
import json
import sqlite3
import time

class TaskQueue:
    path = None
    db = None
    MAX_RETRIES = 20

    ensure_backlog_exists = 'CREATE TABLE IF NOT EXISTS backlog (work text UNIQUE)'
    push_work = 'INSERT INTO backlog (work) VALUES (?)'
    get_work = 'SELECT rowid, work FROM backlog'
    remove_work = 'DELETE FROM backlog WHERE rowid=?'

    ensure_status_exists = 'CREATE TABLE IF NOT EXISTS status (active int UNIQUE)'
    declare_active = 'INSERT INTO status (active) VALUES (1)'
    declare_inactive = 'DELETE FROM status'

    def __init__(self, debug=False):
        self.debug = debug
        if not self.path:
            raise NotImplemented('The path property has not been implemented.')

    def process(self, work):
        raise NotImplemented('The process method has not been implemented.')

    def push(self, *backlog):
        self.db = sqlite3.connect(self.path)
        self._execute(self.ensure_backlog_exists)
        for work in backlog:
            try:
                self._execute(self.push_work, json.dumps(work))
            except sqlite3.IntegrityError as e:
                self.log('ignoring duplicate work')
        self.db.close()

    def start(self):
        pid = os.fork()
        if pid > 0:
            return
        # Detach the forked process from the parent.
        os.setsid()
        self.db = sqlite3.connect(self.path)
        try:
            self._execute(self.ensure_backlog_exists)
            self._execute(self.ensure_status_exists)
            self.log('activating')
            self._execute(self.declare_active)
            self._loop()
            self.log('deactivating')
            self._execute(self.declare_inactive)
        except sqlite3.IntegrityError as e:
            self.log('another worker is already active')
        finally:
            self.db.close()
            self.log('exiting')
            exit(0)

    def log(self, *args):
        if self.debug:
            message = ' '.join(str(arg) for arg in args)
            print('[{}] {}'.format(os.getpid(), message))

    def _wait(self, tries):
        return 0.1*(tries**2)

    def _execute(self, command, *args):
        tries = 0
        last_exception = None
        while tries < self.MAX_RETRIES:
            try:
                result = self.db.execute(command, args)
                self.db.commit()
                return result
            except sqlite3.OperationalError as e:
                last_exception = e
                tries += 1
                wait = self._wait(tries)
                self.log(e)
                self.log('retrying in', wait, 'seconds')
                time.sleep(wait)
        raise last_exception

    def _loop(self):
        try:
            while True:
                backlog = self._execute(self.get_work).fetchone()
                if not backlog:
                    self.log('backlog empty')
                    break
                id, data = backlog
                self.log('processing', id)
                work = json.loads(data)
                self.process(work)
                self.log('deleting', id)
                self._execute(self.remove_work, id)
        except Exception as e:
            self.log(e)
