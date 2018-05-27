from datetime import datetime, timedelta

import requests

import settings


def _previous_month(dt):
    return datetime(dt.year, dt.month, 1) - timedelta(days=1)


def _index_months(months_ago=0):
    month = datetime.now()
    months_removed = 0
    while months_removed != months_ago:
        month = _previous_month(month)
        months_removed = months_removed + 1
    return month.strftime("crawl-%Y-%m")


def point_to_new_indexes():
    """ Removes any existing alias of latest-crawl, looking at the indexes that
        correspond to the last 3 months, and creates a new one for the current month
    """

    es_aliases_url = "{}_aliases?pretty".format(settings.ES_URL)

    # Include current month to avoid a 404 in case the alias points already to current
    actions_json = {
        "actions": []
    }
    for i in (2, 1, 0):
        cmd = {
            "remove": {
                "index": _index_months(i),
                "alias": "latest-crawl"
            }
        }
        actions_json["actions"].append(cmd)

    header = {
        'Content-Type': 'application/json'
    }

    print("Removing old latest-crawl alias")
    resp = requests.post(es_aliases_url, json=actions_json, headers=header)
    print(resp.text)

    cmd = {
        "add": {
            "index": _index_months(0),
            "alias": "latest-crawl"
        }
    }
    actions_json = {
        "actions": [cmd]
    }
    print("Making new alias: latest-crawl -> {0}".format(_index_months(0)))
    resp = requests.post(es_aliases_url, json=actions_json, headers=header)
    print(resp.text)


if __name__ == '__main__':
    point_to_new_indexes()
