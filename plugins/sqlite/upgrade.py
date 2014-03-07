#!/usr/bin/env python3
#
# num: _end, _start, _item, _avg, _min, _max, _on

import logging


logger = logging.getLogger('')


def Upgrade(db, version):
    if version == 1:
        logger.warning("SQLite: dropping history!")
        db.execute("DROP TABLE history;")
        db.execute("DROP INDEX IF EXISTS idx;")
        db.execute("DROP INDEX IF EXISTS idy;")
    elif version == 2:
        # history: time, item, avg, vmin, vmax, power
        logger.info("SQLite: upgrading database.")
        db.execute("DROP INDEX IF EXISTS idy;")
        for item in db.execute("SELECT item FROM history GROUP BY item;").fetchall():
            end = 0
            for row in db.execute("SELECT * FROM history WHERE item='{}' ORDER BY time DESC;".format(item[0])).fetchall():
                time, item, avg, vmin, vmax, power = row
                if end:
                    insert = (time, item, end - time, avg, vmin, vmax, power)
                    db.execute("INSERT INTO num VALUES (?,?,?,?,?,?,?);", insert)
                end = time
        db.execute("DROP TABLE history;")
    elif version == 3:
        #_start, _item, _dur, _avg, _min, _max, _on
        pass
    db.execute("VACUUM;")
    db.commit()
