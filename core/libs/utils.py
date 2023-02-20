"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
def filter_empty_kvs(d: dict):
    empty_k_list = []
    for k in d:
        if not d[k]:
            empty_k_list.append(k)

    for k in empty_k_list:
        del d[k]

    return d