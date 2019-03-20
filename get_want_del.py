import datetime
import json
import os
import re

import requests

project_list = ["mxnet"]


def main():
    os.makedirs("want_del", exist_ok=True)

    for project in project_list:
        one_project(project)
    pass


def one_project(project_name):
    must_find = ["win_amd64", "manylinux1_x86_64", "macosx"]
    mxnet_json_str = requests.get('https://pypi.org/pypi/{0}/json'.format(project_name))
    mxnet_json = json.loads(mxnet_json_str.text)
    releases = mxnet_json["releases"]
    bucket = {}
    bucket_list = []
    today = datetime.datetime.today()
    for release_k in releases:
        match_obj = re.match(".*?b([0-9]{8})", release_k, flags=0)
        if not match_obj:
            continue
        date = datetime.datetime.strptime(match_obj.group(1), "%Y%m%d")
        year_week = (date.isocalendar()[0], date.isocalendar()[1])
        if year_week not in bucket:
            bucket[year_week] = []
            bucket_list.append(year_week)
        bucket[year_week].append((date, release_k))

    with open("want_del/{0}.txt".format(project_name), "w", encoding="utf-8") as obj:
        for year_week in bucket_list:
            data_first_week = datetime.datetime.strptime('{0} {1} 1'.format(*year_week), '%G %V %u')
            if (today - data_first_week).days <= 97:
                continue

            year_week_list = bucket[year_week]
            if len(year_week_list) == 1:
                obj.write("{0}\tgood\tkeep\n".format(year_week_list[0][1]))
                continue
            year_week_list.sort(key=lambda e: e[0])
            out_list = []
            is_find_keep = False
            for item in reversed(year_week_list):
                release = releases[item[1]]
                find_set = set()
                for release_item in release:
                    filename = release_item["filename"]
                    for f in must_find:
                        if f in filename:
                            find_set.add(f)
                if len(find_set) == len(must_find):
                    if is_find_keep:
                        out_list.append((item[1], "good", "delete"))
                    else:
                        is_find_keep = True
                        out_list.append((item[1], 'good', "keep"))
                else:
                    out_list.append((item[1], "bad ", "delete"))
            if not is_find_keep:
                for i in reversed(out_list):
                    obj.write("{0}\t{1}\terror\n".format(i[0],i[1]))
            else:
                for i in reversed(out_list):
                    obj.write("{0}\t{1}\t{2}\n".format(*i))


if __name__ == '__main__':
    main()
