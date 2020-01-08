#!/usr/bin/env python3

import config
import requests
import sqlite3
from datetime import date
from gazette import iulaan_search

DB_CONN = None


def post_message_tg(message_text, chat_id=config.TG_CHAT_ID):
    data = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    r = requests.post(config.TG_URL_SEND, data)
    return r.json()


def insert_iulaan_db(item):
    global DB_CONN
    with DB_CONN:
        DB_CONN.execute("INSERT INTO iulaan(id,title,url,vendor,vendor_url,info) VALUES(?,?,?,?,?,?)", (
            item['id'],
            item['title'],
            item['url'],
            item['vendor'],
            item['vendor_url'],
            "\n".join(item['info'])
        ))


def item_exists(item_id):
    global DB_CONN
    with DB_CONN:
        return DB_CONN.execute("SELECT * FROM iulaan WHERE id = ?", (item_id,)).fetchone()


def init_db():
    global DB_CONN
    DB_CONN = sqlite3.connect(config.PERSIST_DB)

    # table create just in case
    with DB_CONN:
        DB_CONN.execute("CREATE TABLE IF NOT EXISTS iulaan(id INTEGER PRIMARY KEY ,"
                        " title TEXT, url TEXT, vendor TEXT, vendor_url TEXT, info TEXT)")


def format_job(item):
    return \
        "[{}]({})\n\n{}\n{}".format(
            item['title'],
            item["url"],
            item['vendor'],
            "\n".join([x for x in item['info']]))


def fetch_jobs(category=config.JOB_CATEGORIES['tech'], iulaan_type=config.IULAAN_TYPES['jobs'], description=None):
    rep = []
    page = 1
    while page < 5:
        spam = iulaan_search(iulaan_type=iulaan_type,
                             category=category,
                             start_date=date.today().strftime("%d-%m-%Y"),
                             page=page,
                             description=description,
                             open_only=1)
        rep.extend(spam)
        if len(spam) < 15:
            break
        else:
            page += 1

    return rep


def post_iulaan_queue(rep):
    for job in rep:
        if not item_exists(job['id']):
            r = post_message_tg(format_job(job))
            if r["ok"]:
                insert_iulaan_db(job)


if __name__ == "__main__":
    init_db()

    post_iulaan_queue(fetch_jobs())  # all jobs in "information technology category"

    post_iulaan_queue(fetch_jobs(category=config.JOB_CATEGORIES['all'],
                                 description="ޕްރޮގްރާމަރ"))

    post_iulaan_queue(fetch_jobs(category=config.JOB_CATEGORIES['all'],
                                 description="ޑިވެލޮޕަރ"))

    post_iulaan_queue(fetch_jobs(category=config.JOB_CATEGORIES['all'],
                                 iulaan_type=config.IULAAN_TYPES['tenders'],
                                 description="ވެބްސައިޓް ފަރުމާ"))

    post_iulaan_queue(fetch_jobs(category=config.JOB_CATEGORIES['all'],
                                 iulaan_type=config.IULAAN_TYPES['tenders'],
                                 description="ވެބްސައިޓް ޑިވެލޮޕް"))

    # when all is done
    post_message_tg("Gazette task update finished for {}".format(date.today().strftime("%d-%m-%Y")),
                    config.TG_ADMIN_CHATID)
