import sqlite3
from time import time
from datetime import datetime


def now(format_=None):
    if format_:
        return datetime.fromtimestamp(time()).strftime(format_)
    return datetime.fromtimestamp(time())

class DBConnection(object):
    def __init__(self, database_file='database.db'):
        self.conn = sqlite3.connect(database_file)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()


class Episode(object):
    COLUMNS = ('filename', 'played', 'tvshow', 'scheduled', 'duration', 'next')

    def __init__(self, filename, **kwargs):
        self._filename = filename
        self._played = 1 if kwargs.get('played', False) else 0
        self._tvshow = kwargs.get('tvshow')
        scheduled = kwargs.get('scheduled')
        if scheduled:
            scheduled = datetime.strptime(scheduled, '%Y-%m-%d %H:%M:%S')
        self._scheduled = scheduled
        self._duration = kwargs.get('duration')
        self._next = kwargs.get('next')


    def save(self):
        columns = 'REPLACE INTO episode' + str(tuple(self.COLUMNS))
        values = 'VALUES (?, ?, ?, ?, ?, ?);'
        with DBConnection() as db:
            db.cursor.execute(columns + values, tuple(self.__dict__.values()))


    @classmethod
    def pick(cls, timeframe=None):
        if not timeframe:
            timeframe = now('%Y-%m-%d %H:%M:%S')
        order_by = "ORDER BY abs(strftime('%s', '"+timeframe+"') - strftime('%s', scheduled))"
        query = "SELECT * FROM episode "+order_by+" LIMIT 1;"
        with DBConnection() as db:
            db.cursor.execute(query)
            db_episode = db.cursor.fetchone()
            if not db_episode:
                raise sqlite3.DatabaseError("No episode was found", timeframe)
            fields = dict(zip(cls.COLUMNS[1:], list(db_episode[1:])))
            return Episode(db_episode[0], **fields)


    @classmethod
    def get(cls, filename):
        with DBConnection() as db:
            db.cursor.execute('SELECT * FROM episode WHERE filename = ?', (filename))
            db_episode = db.cursor.fetchone()
            if not db_episode:
                raise sqlite3.DatabaseError("No episode was found", filename)
            fields = dict(zip(cls.COLUMNS[1:], list(db_episode[1:])))
            return Episode(db_episode[0], **fields)

    def __repr__(self):
        return str({
            'filename': self._filename,
            'played': True if self._played else False,
            'tvshow': self._tvshow,
            'scheduled': self._scheduled,
            'duration': self._duration,
            'next': self._next,
            })

    def next(self):
        if not self._next:
            return None
        return get(self._next)

    @property
    def played(self):
        return self._played == 1

    @played.setter
    def played(self, played):
        if not isinstance(played, bool):
            raise TypeError(played, 'Must be boolean')
        self._played = 1 if played else 0
        with DBConnection() as db:
            db.cursor.execute('UPDATE episode SET played = ? WHERE filename = ?', (self._played, self._filename))

    @property
    def tvshow(self):
        return self._tvshow

    @property
    def filename(self):
        return self._filename

    @property
    def duration(self):
        return self._duration

    @property
    def scheduled(self):
        return self._scheduled

    @scheduled.setter
    def scheduled(self, scheduled):
        if not isinstance(scheduled, str):
            raise TypeError(scheduled, 'Must be string')
        self._scheduled = datetime.strptime(scheduled, '%Y-%m-%d %H:%M:%S')
        with DBConnection() as db:
            db.cursor.execute('UPDATE episode SET scheduled = ? WHERE filename = ?', (self._scheduled, self._filename))


