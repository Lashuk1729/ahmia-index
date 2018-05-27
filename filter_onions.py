# -*- coding: utf-8 -*-
""" Filter some onions from the index """

import sys
import requests

import settings


def print_error_and_quit():
    """Printing the usage information"""

    print("Filters an onion domain from the index.\n")
    print("Usage: python filter_onions.py some.onion")
    print("Example: python filter_onions.py msydqstlz2kzerdg.onion\n")
    sys.exit()


def filter_content(domain):
    """ Bans certain onions """

    url = settings.ES_URL + settings.ES_INDEX  # URL of the new index
    print('\033[1;30m Test that Elasticsearch is available: %s \033[1;m' % url)
    try:
        r = requests.head(url)
    except requests.exceptions.RequestException as e:
        print(e)
        print('\033[1;31m Cannot connect to Elasticsearch (%s)! \033[1;m' % url)
        sys.exit()
    print('\033[1;32m ---> Yes, Elasticsearch is available!\033[1;m')

    query = '{0}/tor/_search?pretty&size=1000&q=domain:"{1}" AND NOT is_banned:1'.format(url, domain)
    print(query)

    r = requests.get(query)
    if r.status_code == 200:
        hits = r.json()["hits"]["hits"]
        total = len(hits)
        if total > 0:
            for index, hit in enumerate(hits):
                if hit['_source']['domain'] == domain:
                    target_url = hit['_source']['url']
                    result = "%d/%d Filtering %s" % (index+1, total, target_url)
                    print('\033[1;30m ' + result + ' \033[1;m')
                    if index > 0:
                        query = settings.ES_URL + hit["_index"] + '/tor/' + hit['_id']
                        requests.delete(query)
                    else:
                        json_data = {
                            "doc": {"is_banned": 1}
                        }
                        query = settings.ES_URL + hit["_index"] + '/tor/' + hit['_id'] + '/_update'
                        requests.post(query, json=json_data)
        else:
            print('\033[1;31m No search results! \033[1;m')
    else:
        print('\033[1;31m Search failed! \033[1;m')
    print('\033[1;32m Filtered the content. \033[1;m')
    print('\033[1;32m You can run this again to remove sites. \033[1;m')


def main():
    """ Read command line arguments """

    try:
        if len(sys.argv) == 2:
            domain = str(sys.argv[1])
            if len(domain) == 22:
                filter_content(domain)
            else:
                print_error_and_quit()
        else:
            print_error_and_quit()
    except Exception as e:
        print(str(e))
        print_error_and_quit()


if __name__ == '__main__':
    main()
