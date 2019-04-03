import json
import os

import pandas as pd
import requests

from cachetools import cached, TTLCache

ip_cache = TTLCache(10000, 4 * 3600)  # TTL is 4 hours
info_cache = TTLCache(5, 5)  # TTL is 5 seconds


@cached(cache=info_cache)
def get_info():
    # block height
    r_block = requests.get("https://elya-explorer-pos.gonspool.com/api/getblockcount")

    # coin total supply
    r_supply = requests.get("https://elya-explorer-pos.gonspool.com/ext/getmoneysupply")

    # Network difficulty
    r_difficulty = requests.get("https://elya-explorer-pos.gonspool.com/api/getdifficulty")

    return {"height": r_block.text, "supply": int(json.loads(r_supply.text)), "diff": r_difficulty.text}


def get_peers():
    url = "https://elya-explorer-pos.gonspool.com/ext/connections"
    r = requests.get(url)
    result = json.loads(r.text)
    assert r.status_code == 200, "HTTP status code was not ok"

    df = pd.DataFrame.from_records(result['data'],
                                   index='address', columns=['address', 'version', 'protocol', 'createdAt'])
    df.index.rename("ip", inplace=True)
    return df


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
    # result['ip'] = result['request']
    del (result['request'])
    return result


def add_locations_to_df(ip_df):
    list_of_ip = ip_df.index.tolist()
    if len(list_of_ip) == 0:
        print('Provided list of IP addresses is empty!')
        return pd.DataFrame()
    cache_file = "locations.csv"
    if os.path.isfile(cache_file):
        df_cache = pd.read_csv(cache_file, index_col=0)
    else:
        df_cache = pd.DataFrame()

    # find those not in cache yet or with empty latitude or longitude
    diff = list(set(list_of_ip) - set(
        df_cache.loc[df_cache['latitude'].notna() & df_cache['longitude'].notna()].index.tolist()))

    # Check if the current list of peers became smaller than we have in cache.
    # cache_extra = list(set(df_cache.index.tolist()) - set(list_of_ip))
    # if len(cache_extra) > 0 and os.path.isfile(cache_file):
    #     df_cache = pd.DataFrame()
    #     os.remove(cache_file)
    # else:
    # if no changes - return the cached table
    if len(diff) == 0:
        return df_cache

    if len(df_cache) > 0:
        df = df_cache
    else:
        df = ip_df
    for ip in diff:
        tmp = get_loc_by_ip(ip)
        # del (tmp['ip'])
        for col in tmp.keys():
            df.loc[ip, col] = tmp[col]

    # overwrite cache file with the new data
    df.to_csv(cache_file)
    return df


if __name__ == '__main__':
    # lst = get_loc_by_ip(get_peers()[0])
    # print(lst)

    # pd.set_option('display.max_columns', 30)
    # peers = get_peers()
    # res = add_locations_to_df(peers)
    # print(res)

    # print(peers)

    # print(df.index.tolist())
    # print(get_loc_by_ip(df.index.tolist()[0]))

    # print(get_info())
    # dff = get_locations_dataframe(get_peers())
    # dff = pd.read_csv("locations.csv", index_col=0)
    # print(dff)
    # print(len(dff))
    # print(list(set(peers) - set(dff.index.tolist())))
    # # dff.to_csv("locations.csv")

    # df = pd.DataFrame({'lkey': ['foo', 'bar', 'baz', 'foo'],
    #                     'value': [1, 2, 3, 5]})
    # df.loc[2, 'ttt'] = 'fds'
    # df.loc[3, 'fff'] = 'rew'
    # print(df)

    cache_file = "locations.csv"
    if os.path.isfile(cache_file):
        df_cache = pd.read_csv(cache_file, index_col=0)
    else:
        df_cache = pd.DataFrame()

    # find those with empty latitude
    df_cache_not_filled = df_cache.loc[df_cache['latitude'].notna() & df_cache['longitude'].notna()].index.tolist()
    print(len(df_cache.index.tolist()))
    print(len(df_cache_not_filled))
