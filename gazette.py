#!/usr/bin/env python3
# scraper for MV Gazette

import requests
import config
from bs4 import BeautifulSoup as bs


def iulaan_search(page=1,
                  iulaan_type=config.IULAAN_TYPES['all'],
                  category=config.JOB_CATEGORIES['all'],
                  open_only=1,
                  start_date=None,
                  description=None):

    return_data = []
    url = "{}{}page/{}".format(config.GAZETTE_BASE_URL, config.IULAAN_SEARCH_URL, page)
    data = {
        "job-category": category,
        "iulaan-type": iulaan_type,
        "open-only": open_only,
        "description": description,
        "start-date": start_date
    }

    response = requests.post(url, data=data)
    if response.status_code==requests.codes.ok:

        soup = bs(response.content, "html.parser")

        items = soup.find_all("div", class_="items")
        for item in items:
            item_body = {}

            # parse the title
            title = item.find("a", class_="iulaan-title")
            item_body["url"] = title.get("href")
            item_body["id"] = [int(segment) for segment in item_body["url"].split("/") if segment.isdigit()][0]
            item_body["title"] = title.text

            # parse the office
            vendor = item.find("a", class_="iulaan-office")
            item_body["vendor"] = vendor.text
            item_body["vendor_url"] = vendor.get("href")

            # parse info
            info = item.find_all("div", class_="info")
            item_body["info"] = [i.text for i in info]

            return_data.append(item_body)


    return return_data


# run some tests
if __name__ == "__main__":
    from pprint import pprint

    limiter = 0
    currpage = 1
    exit = False

    stuff = []
    while currpage < 5 and not exit:

        print("fetching page={}".format(currpage))
        rep = iulaan_search(iulaan_type=config.IULAAN_TYPES['jobs'], category=config.JOB_CATEGORIES['tech'], open_only=0)

        stuff.append(rep)

        if len(rep) < 15:
            break

        for r in rep:
            if r["id"]==limiter:
                exit = True

        currpage += 1

    pprint(stuff)
