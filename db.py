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


class Media:
    COLUMNS = ('filename','scheduled','duration')

    def __init__(self, filename, **kwargs):
        self._name = self.__class__.__name__
        self._filename = filename
        scheduled = kwargs.get('scheduled')
        if scheduled:
            scheduled = datetime.strptime(scheduled, '%Y-%m-%d %H:%M:%S')
        self._scheduled = scheduled
        self._duration = kwargs.get('duration')


    def save(self):
        query = f'REPLACE INTO {self._name} {str(tuple(self.COLUMNS))} VALUES (?, ?, ?);'
        class_values = self.__dict__
        class_values.pop('_name')
        with DBConnection() as db:
            db.cursor.execute(query, tuple(class_values.values()))


    @classmethod
    def pick(cls, timeframe=None):
        if timeframe:
            order_by = f"abs(strftime('%s', '{timeframe}') - strftime('%s', scheduled))"
        else:
            order_by = "RANDOM()"
        query = f"SELECT * FROM {cls.__name__} ORDER BY {order_by} LIMIT 1;"
        with DBConnection() as db:
            db.cursor.execute(query)
            db_result = db.cursor.fetchone()
            if not db_result:
                raise sqlite3.DatabaseError("Not found", timeframe)
            fields = dict(zip(cls.COLUMNS[1:], list(db_result[1:])))
            return Media(db_result[0], **fields)


    def _repr__(self):
        return str({
            'filename': self._filename,
            'scheduled': self._scheduled,
            'duration': self._duration,
        })


    @property
    def scheduled(self):
        return self._scheduled

    @property
    def filename(self):
        return self._filename

    @property
    def duration(self):
        return self._duration

    @scheduled.setter
    def scheduled(self, scheduled):
        if not isinstance(scheduled, str):
            raise TypeError(scheduled, 'Must be string')
        self._scheduled = datetime.strptime(scheduled, '%Y-%m-%d %H:%M:%S')
        with DBConnection() as db:
            classname = self.__class__.__name__
            db.cursor.execute(f'UPDATE {classname} SET scheduled = ? WHERE filename = ?', (self._scheduled, self._filename))


