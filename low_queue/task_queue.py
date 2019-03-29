import os
import pickle
import sqlite3
import time

class TaskQueue:
    path = None
    db = None
    MAX_RETRIES = 20
    SILENT = 0
    ERROR = 1
    WARN = 2
    INFO = 3

    ensure_backlog_exists = 'CREATE TABLE IF NOT EXISTS backlog (work blob UNIQUE)'
    push_work = 'INSERT INTO backlog (work) VALUES (?)'
    get_work = 'SELECT rowid, work FROM backlog'
    remove_work = 'DELETE FROM backlog WHERE rowid=?'

    ensure_status_exists = 'CREATE TABLE IF NOT EXISTS status (active int UNIQUE)'
    declare_active = 'INSERT INTO status (active) VALUES (1)'
    declare_inactive = 'DELETE FROM status'
    declare_inactive_if_empty = 'DELETE FROM status WHERE NOT EXISTS (SELECT * FROM backlog)'
    check_status = 'SELECT active FROM status'

    def __init__(self, log_level=ERROR):
        self.log_level = log_level
        if not self.path:
            raise NotImplemented('The path property has not been implemented.')

    def process(self, work):
        raise NotImplemented('The process method has not been implemented.')

    def push(self, *backlog):
        self.db = sqlite3.connect(self.path)
        self._execute(self.ensure_backlog_exists)
        for work in backlog:
            try:
                data = pickle.dumps(work, pickle.HIGHEST_PROTOCOL)
                self._execute(self.push_work, sqlite3.Binary(data))
            except sqlite3.IntegrityError as e:
                self.info('ignoring duplicate work')
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
            self._loop()
        except sqlite3.IntegrityError as e:
            self.info('another worker is already active')
        finally:
            self.db.close()
            self.info('exiting')
            exit(0)

    def warn(self, *args):
        self.log(self.WARN, *args)

    def info(self, *args):
        self.log(self.INFO, *args)

    def log(self, log_level, *args):
        if log_level <= self.log_level:
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
                self.warn(e)
                self.warn('retrying in', wait, 'seconds')
                time.sleep(wait)
        raise last_exception

    def _loop(self):
        self.info('activating')
        self._execute(self.declare_active)
        try:
            while True:
                # Check the backlog and conditionally deactivate in a single
                # query to ensure the operation is atomic.
                self._execute(self.declare_inactive_if_empty)
                active = self._execute(self.check_status).fetchone()
                if not active:
                    self.info('backlog empty')
                    self.info('deactivated')
                    break
                backlog = self._execute(self.get_work).fetchone()
                id, data = backlog
                self.info('processing', id)
                work = pickle.loads(str(data))
                self.process(work)
                self.info('deleting', id)
                self._execute(self.remove_work, id)
        except Exception as e:
            self.error(e)
            self.error('deactivating')
            self._execute(self.declare_inactive)
