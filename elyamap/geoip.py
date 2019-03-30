import json
import os

import pandas as pd
import requests

from cachetools import cached, TTLCache

ip_cache = TTLCache(10000, 4 * 3600)  # TTL is 4 hours
info_cache = TTLCache(5, 5)  # TTL is 5 seconds


@cached(cache=info_cache)
def get_info(node='139.59.149.46'):
    # {"alt_blocks_count": 2, "difficulty": 21099405,
    #  "fee_address": "eL2aPrdrrupfvKaGNy4PdGM2BvSmxDryDc9GQCzh2idS2WFmZb2RTkdYFcQKvS6Ev575qY3sjg2RH5pf6hD4zovF1jYLuiZD3",
    #  "grey_peerlist_size": 1150, "height": 327860, "incoming_connections_count": 32, "last_known_block_index": 327859,
    #  "outgoing_connections_count": 8, "status": "OK", "tx_count": 371240, "tx_pool_size": 0,
    #  "version": "1.4.9.780 (-dirty)", "white_peerlist_size": 50}

    r2 = requests.get("http://" + node + ":57778/getinfo")
    return json.loads(r2.text)


def get_peers(node='139.59.149.46'):
    # {"peers": ["59.24.131.8:57777", "139.99.40.136:57777", "139.99.100.124:57777", "45.76.251.130:57777",
    #            "158.69.52.139:57777", "167.99.88.231:18080", "45.32.149.166:57777", "80.240.30.245:57777",
    #            "175.123.219.158:57777", "142.196.142.165:57777", "68.2.236.244:57777", "94.54.103.225:57777",
    #            "136.144.202.144:57777", "98.144.1.160:57777", "70.171.170.122:57777", "91.89.61.123:57777",
    #            "211.230.120.149:57777", "67.149.205.207:57777", "80.211.241.70:57777", "84.41.39.24:57777",
    #            "109.167.163.66:57777", "59.28.63.147:57777", "219.251.192.163:57777", "115.79.146.46:57777",
    #            "90.146.49.246:57777", "59.28.237.100:57777", "39.32.8.208:57777", "134.215.173.9:57777",
    #            "42.118.66.127:57777", "175.214.11.134:57777", "210.211.124.189:57777", "91.114.173.217:57777",
    #            "92.249.150.146:57777", "189.70.209.112:57777", "112.153.2.229:57777", "88.214.241.183:57777",
    #            "176.121.240.8:57777", "97.120.150.90:57777", "47.254.33.204:57777", "220.86.168.90:57777",
    #            "39.115.219.55:57777", "112.165.98.190:57777", "217.162.58.109:57777", "78.153.49.209:57777",
    #            "194.85.135.154:57777", "220.86.168.181:57777", "212.92.101.159:23021", "94.130.67.112:57777",
    #            "159.65.52.155:57777", "138.197.219.100:30554"], "status": "OK"}

    r = requests.get("http://" + node + ":57778/peers")
    # print(r.text)
    result = json.loads(r.text)
    assert r.status_code == 200, "HTTP status code was not ok"
    assert result['status'] == "OK", "Elya node response was not OK!"

    return [ip.rsplit(":")[0] for ip in result['peers']]


@cached(cache=ip_cache)
def get_loc_by_ip(ip):
    url = "http://www.geoplugin.net/json.gp?ip="
    # http://www.geoplugin.net/json.gp?ip=139.59.149.46

    # {
    #     "geoplugin_request": "98.144.1.160",
    #     "geoplugin_status": 200,
    #     "geoplugin_delay": "1ms",
    #     "geoplugin_credit": "Some of the returned data includes GeoLite data created by MaxMind, available from <a href='http:\/\/www.maxmind.com'>http:\/\/www.maxmind.com<\/a>.",
    #     "geoplugin_city": "Milwaukee",
    #     "geoplugin_region": "Wisconsin",
    #     "geoplugin_regionCode": "WI",
    #     "geoplugin_regionName": "Wisconsin",
    #     "geoplugin_areaCode": "",
    #     "geoplugin_dmaCode": "617",
    #     "geoplugin_countryCode": "US",
    #     "geoplugin_countryName": "United States",
    #     "geoplugin_inEU": 0,
    #     "geoplugin_euVATrate": false,
    #     "geoplugin_continentCode": "NA",
    #     "geoplugin_continentName": "North America",
    #     "geoplugin_latitude": "42.9956",
    #     "geoplugin_longitude": "-88.0422",
    #     "geoplugin_locationAccuracyRadius": "5",
    #     "geoplugin_timezone": "America\/Chicago",
    #     "geoplugin_currencyCode": "USD",
    #     "geoplugin_currencySymbol": "$",
    #     "geoplugin_currencySymbol_UTF8": "$",
    #     "geoplugin_currencyConverter": 1
    # }

    r = requests.get(url + ip)
    resp = json.loads(r.text)
    print("Status code for IP {} was {}".format(resp['geoplugin_request'], r.status_code))

    result = {key.replace("geoplugin_", ""): resp[key] for key in resp.keys()}
    del (result['status'])
    del (result['delay'])
    del (result['credit'])
    result['ip'] = result['request']
    del (result['request'])
    return result


def get_locations_dataframe(list_of_ip):
    if len(list_of_ip) == 0:
        print('Provided list of IP addresses is empty!')
        return pd.DataFrame()
    cache_file = "locations.csv"
    if os.path.isfile(cache_file):
        df_cache = pd.read_csv(cache_file, index_col=0)
    else:
        df_cache = pd.DataFrame()

    # TODO: Check if the current list of peers became smaller.
    # In this case maybe we need to verify if these 'extra nodes' are online
    # e.g. knock the network port
    diff = list(set(list_of_ip) - set(df_cache.index.tolist()))

    # if no changes - return the cached table
    if len(diff) == 0:
        return df_cache

    if len(df_cache) > 0:
        df = df_cache
    else:
        df = pd.DataFrame.from_records([get_loc_by_ip(list_of_ip[0])], index='ip')
    for ip in diff:
        if ip not in df.index:
            tmp = get_loc_by_ip(ip)
            df = df.append(pd.DataFrame.from_records([tmp], index='ip'), verify_integrity=True)

    # overwrite cache file with the new data
    df.to_csv(cache_file)
    return df


if __name__ == '__main__':
    # lst = get_loc_by_ip(get_peers()[0])
    # print(lst)

    # peers = get_peers()
    # print(peers)
    dff = get_locations_dataframe(get_peers())
    # dff = pd.read_csv("locations.csv", index_col=0)
    print(dff)
    print(len(dff))
    # print(list(set(peers) - set(dff.index.tolist())))
    # # dff.to_csv("locations.csv")
