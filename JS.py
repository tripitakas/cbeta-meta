#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import csv
from os import path
from operator import itemgetter

txt_file = path.join(path.dirname(__file__), 'JS.txt')
csv_file = path.join(path.dirname(__file__), 'Sutra-JS.csv')

# unified_sutra_code UN00247
# sutra_code GL0002
# name 放光般若波羅蜜經
# due_reel_count 20
# existed_reel_count 20
# author
# trans_time
# start_volume GL_2_1
# start_page 1
# end_volume GL_2_20
# end_page 33
# remark
# 编号	标题	译者全称	译者	册	起始頁
# 	六百卷	唐三藏法师玄奘奉诏译	玄奘译	3	1

rows = open(txt_file).read().replace('\u2003', '')
rows = [s.split('\t') for s in re.sub(r'"(.|\n)+?"', lambda m: m.group().split('\n')[0], rows).split('\n')]
sutras, last_code = {}, ''

for i, r in enumerate(rows):
    if len(r) < 6:
        continue
    name = re.search(r'^(.+?)（', r[1])
    if name:
        name = name[1]
    else:
        name = re.search(r'^(.+?)[一二三四五六七八九十]+卷', r[1])
        if name:
            name = name[1]
    name = name or r[1]
    r[1] = re.sub(r'）.+$', '）', re.sub(r'卷\s*附', '卷', r[1]))
    r.append(name)
    if not r[0] and not sutras.get(name):
        print(r)  # 经名略有差异，经号为空
    r[0] = (' ' * 5 + (r[0] + ' ' if r[0] else last_code + 'B'))[-6:]
    last_code = r[0][:-1]
    sutra = sutras[name] = sutras.get(name) or dict(code=r[0], items=[])
    sutra['items'].append(r)

codes = set()
for name, sutra in sutras.items():
    codes.add(sutra['code'])

for code in sorted(list(codes)):
    for name, sutra in sutras.items():
        if sutra['code'] != code:
            continue
        if len(sutra['items']) > 1:
            print('%s\t%s\t%s' % (code, name, '\t'.join([r[1].replace(name, '') for r in sutra['items']])))
for i, r in enumerate(rows):
    if len(r) < 7:
        continue
    name, sutra = r[6], sutras[r[6]]
    item = dict(name=r[1])
    author = r

sutras = sorted(list(sutras.items()), key=itemgetter(0))
output = [['unified_sutra_code', 'sutra_code', 'name', 'due_reel_count', 'existed_reel_count', 'author',
           'trans_time', 'start_volume', 'start_page', 'end_volume', 'end_page', 'remark']]
for sutra in sutras:
    sutra[1]['code'] = sutra[1]['code'].strip()
    for r in sutra[1]['items']:
        r.pop(0)
    if len(sutra[1]['items']) > 1:
        print(sutra)
