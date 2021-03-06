__author__ = 'LeoDong'
import MySQLdb

import MySQLdb.cursors

import config
import tool
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
db_con = None


def db_connect():
    """
    connect DB
    :return: db connection
    """
    global db_con
    if db_con is None:
        db_con = MySQLdb.connect(host=config.db_host,
                                 user=config.db_user,
                                 passwd=config.db_pass,
                                 db=config.db_name,
                                 cursorclass=MySQLdb.cursors.DictCursor)
        db_con.autocommit(on=True)
    return db_con


def db_close():
    """
    close the db connection
    :return:
    """
    global db_con
    db_con.close()


def get_all_urls():
    """
    get all urls in url_lib
    :return:
    """
    sql = """SELECT url FROM url_lib"""
    c = db_connect().cursor()
    c.execute(sql)
    res = c.fetchall()
    c.close()
    return [x['url'] for x in res]


def get_all_ids_known():
    """
    get all targeted urls in url_lib
    :return:
    """
    sql = """SELECT id FROM url_lib WHERE is_target != %s """
    c = db_connect().cursor()
    c.execute(sql, (config.const_IS_TARGET_UNKNOW,))
    res = c.fetchall()
    c.close()
    return [x['id'] for x in res]


def get_all_ids_istarget():
    """
    get all targeted urls in url_lib
    :return:
    """
    sql = """SELECT id FROM url_lib WHERE is_target IN (%s,%s) """
    c = db_connect().cursor()
    c.execute(sql, (config.const_IS_TARGET_UNKNOW, config.const_IS_TARGET_NO))
    res = c.fetchall()
    c.close()
    return [x['id'] for x in res]


def get_url_by_id(id):
    """
    get a url associated with an id
    :param id:
    :return:
    """
    sql = """SELECT * FROM url_lib WHERE id = %s"""
    c = db_connect().cursor()
    c.execute(sql, (id,))
    res = c.fetchone()
    c.close()
    return res


def get_url_by_url(url):
    """
    get a url item associated with an url
    :param url:
    :return:
    """
    sql = """SELECT * FROM url_lib WHERE url = %s"""
    c = db_connect().cursor()
    c.execute(sql, (url,))
    res = c.fetchone()
    c.close()
    return res


def general_update_url(id, is_target, content_hash, layout_hash, extractor, title, content_type):
    sql = """
    UPDATE url_lib SET is_target=%s, content_hash=%s, layout_hash =%s, extractor =%s, title=%s, content_type=%s WHERE id=%s
    """
    c = db_connect().cursor()
    c.execute(sql, (is_target, content_hash, layout_hash, extractor, title, content_type, id,))
    c.close()


def general_insert_url(url, is_target, content_hash, layout_hash, extractor, title, content_type):
    sql = """
    INSERT INTO url_lib (url, is_target, content_hash, layout_hash, extractor, title, content_type)
      VALUES (%s, %s,%s, %s, %s, %s, %s)
    """
    c = db_connect().cursor()
    c.execute(sql, (url, is_target, content_hash, layout_hash, extractor, title, content_type))
    lid = c.lastrowid
    c.close()
    return lid


def new_url_insert(url):
    """
    create a new url item
    :param url:
    :param title:
    :param content_hash:
    :param layout_hash:
    :return:
    """
    return general_insert_url(url, config.const_IS_TARGET_UNKNOW, "", "", tool.extractor2str(config.const_RULE_UNKNOW),
                              "", "")


def exist_url_content_update(id, title, content_hash, layout_hash, content_type):
    """
    update an url item `title` `content_hash` `layout_hash` `last_access_ts`
    :param id:
    :param title:
    :param content_hash:
    :param layout_hash:
    :return:
    """
    sql = """UPDATE url_lib SET title=%s, content_hash=%s, layout_hash =%s, content_type=%s WHERE id=%s """
    c = db_connect().cursor()
    c.execute(sql, (title, content_hash, layout_hash, content_type, id))
    c.close()


def update_url_lastaccessts(id):
    """
    update an url item "last_access_ts" only
    :param id:
    :return:
    """
    sql = """UPDATE url_lib SET last_access_ts=current_timestamp() WHERE id=%s"""
    c = db_connect().cursor()
    c.execute(sql, (id,))
    c.close()


def update_url_lastextractts(id):
    """
    update an url item "last_access_ts" only
    :param id:
    :return:
    """
    sql = """UPDATE url_lib SET last_extract_ts=current_timestamp() WHERE id=%s"""
    c = db_connect().cursor()
    c.execute(sql, (id,))
    c.close()


def delete_sem_with_urlid(id):
    """
    delete seminar information with a specific url id
    :param id:
    :return:
    """
    sql = """DELETE FROM sem_info WHERE url_id=%s"""
    c = db_connect().cursor()
    c.execute(sql, (id,))
    c.close()


def reset_db():
    """
    reset db:
    clear and reset auto-increment of url_lib
    :return:
    """
    sql = """TRUNCATE TABLE url_lib"""
    c = db_connect().cursor()
    c.execute(sql)
    c.close()


def new_sem_with_map(url_id, info):
    keys = info.keys()
    values = info.values()
    newvalues=[]
    for i in values:
        if isinstance(i, unicode):
            newvalues.append(i.encode('utf-8'))
        else:
            if i is None:
                newvalues.append("")
            else:
                newvalues.append(i)
    values = newvalues
    sql = """
    INSERT INTO sem_info (url_id, %s) VALUES (%s,%s)
    """
    c = db_connect().cursor()
    sql = sql % (",".join(keys), url_id, ",".join(["'" + MySQLdb.escape_string(x) + "'" for x in values]))
    c.execute(sql)
    c.close()


def get_url_with_same_layout_hash(hash):
    sql = """SELECT id, extractor FROM url_lib WHERE layout_hash = %s """
    c = db_connect().cursor()
    c.execute(sql, (hash,))
    res = c.fetchall()
    c.close()
    maps = dict()
    for x in res:
        if x['extractor']!="[-1]":
            maps[x['extractor']] = maps.get(x['extractor'], 0) + 1
    return len(res), maps


def get_seminar_all():
    sql = """select sem_info.*, url_lib.url from sem_info join url_lib on sem_info.url_id=url_lib.id"""
    c = db_connect().cursor()
    c.execute(sql, ())
    res = c.fetchall()
    return res