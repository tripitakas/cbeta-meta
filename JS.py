#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import csv
import sys
from os import path
from operator import itemgetter

txt_file = path.join(path.dirname(__file__), 'JS.txt')
csv_file = path.join(path.dirname(__file__), 'Sutra-JS.csv')
volume_file = path.join(path.dirname(__file__), 'Volume-JS.csv')

# txt的各列：编号	标题	译者全称	译者	册	起始頁
# 1	六百卷	唐三藏法师玄奘奉诏译	玄奘译	3	1

rows = open(txt_file).read().replace('\u2003', '')
rows = [s.split('\t') for s in re.sub(r'"(.|\n)+?"', lambda m: m.group().split('\n')[0], rows).split('\n')]
sutras, last_code = {}, ''

for i, r in enumerate(rows):
    if len(r) < 6:
        continue
    sutra_name = re.search(r'^(.+?)（', r[1])  # 取（ 前的文字
    if sutra_name:
        sutra_name = sutra_name[1]
    else:
        sutra_name = re.search(r'^(.+?)[一二三四五六七八九十]+卷', r[1])  # 取多少卷之前的文字
        if sutra_name:
            sutra_name = sutra_name[1]
    r[1] = re.sub(r'）.+$', '）', re.sub(r'卷\s*附', '卷', r[1]))  # 经名去掉末尾的说明
    sutra_name = sutra_name or r[1]
    r.append(sutra_name)  # 记下经名前缀

    last_code = r[0] = (' ' * 5 + (r[0] or last_code))[-6:]
    sutra_name = r[0] + sutra_name
    sutras[sutra_name] = sutras.get(sutra_name) or dict(code=r[0], items=[])
    sutras[sutra_name]['items'].append(r)  # items: 同一部经论里的条目

    # 起始页转为图片页号
    r[5] = (int(r[5]) - 1) * 2 + 1

codes = set(sutra['code'] for name, sutra in sutras.items())

for code in sorted(list(codes)):
    for sutra_name, sutra in sutras.items():
        if sutra['code'] != code:
            continue
        sutra_name = sutra_name.replace(code, '')
        if len(sutra['items']) > 1:
            print('%s\t%s\t%s' % (code, sutra_name, '\t'.join([r[1].replace(sutra_name, '') for r in sutra['items']])))

for i, r in enumerate(rows):
    if len(r) < 7:
        continue
    sutra_name, sutra = r[6], sutras[r[0] + r[6]]
    item = dict(name=r[1])
    author = r

sutras = sorted(list(sutras.items()), key=itemgetter(0))
output_sutra = [['unified_sutra_code', 'sutra_code', 'sutra_name', 'due_reel_count', 'existed_reel_count',
                 'author', 'trans_time', 'start_volume', 'start_page', 'end_volume', 'end_page', 'remark']]
nums = '○一二三四五六七八九十百上中下之'


def text_to_num(text):
    m = re.search(r'^[○一二三四五六七八九十百]+', text)
    if m:
        num = 0
        for t in m.group():
            t = nums.index(t)
            if t == 10:
                t = 0 if num else 10 if len(m.group()) == 1 else 1
            elif t == 11:
                num *= 100
                continue
            num = num * 10 + t
        # print('%s: %d' % (m.group(), num))
        return num
    t = re.sub('[○一二三四五六七八九十百]([上中下之].*)?', '', text)
    return t


for sutra in sutras:
    sutra[1]['code'] = sutra[1]['code'].strip()
    sutra[1]['prefix'] = re.sub(r'^\s*\d+', '', sutra[0])
    sutra = sutra[1]
    for r in sutra['items']:
        r.pop(0)
        r[0] = r[0].replace(sutra['prefix'], '')

    sutra_code = 'JS%04d' % int(sutra['code'])
    sutra_name = sutra['prefix']
    reels, volumes, pages = [], [], []  # 卷，册，页
    translators = set()

    for i, r in enumerate(sutra['items']):
        m1 = re.search(r'（?卷[之]?([{0}]+)至卷[之]?([{0}]+)）?'.format(nums), r[0])
        m2 = len(sutra['items']) == 1 and re.search(r'([{0}]+)卷'.format(nums), sutra_name)
        m3 = m2 or re.search(r'存?([{0}]+)卷'.format(nums), r[0]) or re.search(r'存?卷([{0}]+)'.format(nums), r[0])
        if m1:
            a, b = text_to_num(m1.group(1)), text_to_num(m1.group(2))
            reels.extend(range(int(a), int(b) + 1))
        elif m3:
            m3 = text_to_num(m3.group(1))
            if isinstance(m3, int):
                reels.extend(range(1, 1 + m3))
            else:
                reels.append(1 + i)
        elif r[0]:
            if sutra_name == '云栖法汇':  # 11卷
                reels.extend(range(1, 12))
            else:
                reels.append(1 + i)

        volumes.append(r[3])
        translators.add(r[2])
    reels = sorted(list(set(reels))) or [1]
    volumes = sorted(list(set(volumes)))
    start_volume = 'JS_' + volumes[0]  # 起始册
    end_volume = 'JS_' + volumes[-1]  # 终止册
    start_page = sutra['items'][0][4]  # 起始页号（图片号）

    if len(sutra['items']) > 1:
        print('%s\t%s\t%d条\t%d卷\t%d册' % (sutra_code, sutra_name, len(sutra['items']), len(reels), len(volumes)))
        for r in sutra['items']:
            print('\t%s\t%s\t%s册\tP%s' % (r[0], r[2], r[3], r[4]))  # 卷别,译者,册,起始页

    output_sutra.append([
        '',  # unified_sutra_code
        sutra_code,
        sutra_name,
        len(reels),  # due_reel_count
        len(reels),  # existed_reel_count
        list(translators)[0],  # author
        '',  # trans_time
        start_volume,
        start_page,
        end_volume,
        0,  # end_page
        '',  # remark
    ])

# 得到每册的页数（即图片数，不是经目里的页）
with open(volume_file) as f:
    pages_volume = {r[0]: len(r[5].split(',')) for r in csv.reader(f) if '_' in r[0]}

# 如果下一部经的start_volume与当前经的end_volume在同一册，则可直接推断（下一部经起始页的上一页即当前经的最后一页），不需要依靠Volume信息。
# 如果下一部经在另一册的第一页或当前经是最后一册，那么当前经应该在本册的最后一页，这个时候需要用到Volume信息。
for sutra_i, sutra in enumerate(output_sutra[1:]):
    next_sutra = sutra_i + 2 < len(output_sutra) and output_sutra[sutra_i + 2]
    end_volume = sutra[-3]  # 当前经的最后一册
    if next_sutra and next_sutra[-5] == sutra[-5]:  # 在同一册
        sutra[-2] = next_sutra[-4] - 1  # 下一部经起始页的上一页即当前经的最后一页
    elif end_volume in pages_volume:
        sutra[-2] = pages_volume[end_volume]  # 当前经应该在本册的最后一页
    else:
        sys.stderr.write('%s page not exist' % (end_volume,))

# 导出Sutra-JS.csv
with open(csv_file, 'w') as f:
    csv.writer(f).writerows(output_sutra)
