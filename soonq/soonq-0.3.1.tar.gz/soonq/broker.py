"""Implements broker classes.

Classes:
Broker
"""

import datetime as dt
import pickle
import sqlite3

from .config import DB_PATH, QUEUE_TABLENAME, WORK_TABLENAME


class Broker:
    """Implements a basic FIFO queue using SQLite.
    """

    def enqueue(self, item, queue_name):
        """Enqueue the given item in the queue with the given name."""
        con = sqlite3.connect(str(DB_PATH))
        with con:
            c = con.execute(
                f"""
                SELECT position
                FROM {QUEUE_TABLENAME}
                ORDER BY position DESC
                """
            )
            max_position = c.fetchone()  # Returns a tuple.
            new_position = max_position[0] + 1 if max_position else 0
            # Serialize objects to be stored as BLOB.
            item['args'] = pickle.dumps(
                item['args'], protocol=pickle.HIGHEST_PROTOCOL)
            item['kwargs'] = pickle.dumps(
                item['kwargs'], protocol=pickle.HIGHEST_PROTOCOL)
            con.execute(
                f"""
                INSERT INTO {QUEUE_TABLENAME} (
                    task_id,
                    queue_name,
                    position,
                    published,
                    args,
                    kwargs
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    item['task_id'], queue_name, new_position,
                    dt.datetime.now(), item['args'], item['kwargs'],
                ),
            )
        con.close()

    def dequeue(self, queue_name):
        """Dequeue the next item (item with lowest position number) from
        the queue with the given name and return it.
        """
        con = sqlite3.connect(str(DB_PATH))
        con.row_factory = sqlite3.Row
        with con:
            c = con.execute(
                f"""
                SELECT
                    task_id,
                    queue_name,
                    position,
                    published,
                    args,
                    kwargs
                FROM {QUEUE_TABLENAME}
                WHERE queue_name = ?
                ORDER BY position ASC
                """,
                (queue_name,),
            )
            dequeued_item = c.fetchone()
            if dequeued_item:
                item_id = dequeued_item['task_id']
                con.execute(
                    f"""
                    DELETE FROM {QUEUE_TABLENAME}
                    WHERE task_id = ?
                    """,
                    (item_id,),
                )
        con.close()
        return dequeued_item

    def add_work(self, item, status):
        """Add the given item to the work table."""
        con = sqlite3.connect(str(DB_PATH))
        with con:
            con.execute(
                f"""
                INSERT INTO {WORK_TABLENAME} (
                    task_id,
                    queue_name,
                    started,
                    status
                )
                VALUES (?, ?, ?, ?)
                """,
                (item.task_id, item.task_name, dt.datetime.now(), status),
            )
        con.close()

    def remove_work(self, item):
        """Remove the given item from the work table."""
        con = sqlite3.connect(str(DB_PATH))
        with con:
            con.execute(
                f"""
                DELETE FROM {WORK_TABLENAME}
                WHERE task_id = ?
                """,
                (item.task_id,),
            )
        con.close()

    def update_status(self, item, status):
        """Update the status of the given item in the work table."""
        con = sqlite3.connect(str(DB_PATH))
        with con:
            con.execute(
                f"""
                UPDATE {WORK_TABLENAME}
                SET status = ?
                WHERE task_id = ?
                """,
                (status, item.task_id),
            )
        con.close()

    def update_exc_info(self, item, type_, value, traceback):
        """Update exception info for the given item."""
        con = sqlite3.connect(str(DB_PATH))
        # Serialize objects to be stored as BLOB.
        ptype = pickle.dumps(type_, protocol=pickle.HIGHEST_PROTOCOL)
        pvalue = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        ptraceback = pickle.dumps(traceback, protocol=pickle.HIGHEST_PROTOCOL)
        with con:
            con.execute(
                f"""
                UPDATE {WORK_TABLENAME}
                SET
                    exc_type = ?,
                    exc_value = ?,
                    exc_traceback = ?
                WHERE task_id = ?
                """,
                (ptype, pvalue, ptraceback, item.task_id),
            )
        con.close()
