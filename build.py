#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
import sys
import csv
import json
import re

meta_path = '../cbeta-metadata'
cache = {}

canon_names = {
    'A': '趙城金藏',
    'B': '補編',
    'C': '中華藏',
    'D': '國圖',
    'F': '房山石經',
    'G': '佛教大藏經',
    'GA': '志彙',
    'GB': '志叢',
    'I': '佛拓',
    'J': '嘉興藏',
    'K': '高麗藏',
    'L': '乾隆藏',
    'M': '卍正藏',
    'N': '南傳',
    'P': '永樂北藏',
    'Q': '磧砂藏',
    'R': '卍續藏',
    'S': '宋藏遺珍',
    'T': '大正藏',
    'U': '洪武南藏',
    'X': '卍續',
    'Y': '印順',
    'Z': '卍大日本續藏經',
    'ZS': '正史',
    'ZW': '藏外'
}


def load_json(filename, def_value=None):
    try:
        if path.exists(filename):
            with open(filename) as f:
                return json.load(f)
    except ValueError as e:
        sys.stderr.write('Fail to load %s: %s\n' % (filename, str(e)))
    return def_value


def load_csv(filename):
    if path.exists(filename):
        with open(filename) as f:
            return list(csv.reader(f))


def save_csv(rows, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            c = csv.writer(f)
            c.writerows(rows)
            return True
    except IOError as e:
        sys.stderr.write('Fail to save %s: %s\n' % (filename, str(e)))


def build_meta():
    all_title_file = path.join(meta_path, 'titles', 'all-title-byline.csv')
    titles = load_csv(all_title_file)[1:]
    items = ['经号,经名,所属藏经,部类,册别,卷数,作译者,时间'.split(',')]

    for work_id, title, extent, author in titles:  # 典籍編號,典籍名稱,卷數,作譯者
        canon_code = re.search('^([A-Z]{1,2})', work_id).group()
        if canon_code not in canon_names and len(canon_code) > 1:
            canon_code = canon_code[:-1]

        times = cache[canon_code + '_time'] = cache.get(canon_code + '_time') or load_json(
            path.join(meta_path, 'time', 'out', '%s.json' % canon_code), {})
        times, time = times.get(work_id, {}), ''
        dynasty = times.get('dynasty')
        if dynasty and dynasty != author and (len(dynasty) < 3 or not re.search(
                '[造糅譯集述釋頌論說著錄編圖註寫撰譯作製本英薩詩]$|[(（]', dynasty)):
            if times.get('time_from'):
                dynasty += '%s~%s' % (times['time_from'], times['time_to'])
            time = dynasty

        categories = cache[canon_code + '_category'] = cache.get(canon_code + '_category') or load_json(
            path.join(meta_path, 'category', 'work_categories.json'), {})
        category = categories.get(work_id, {}).get('category_names', '')

        id_map = cache[canon_code + '_idmap'] = cache.get(canon_code + '_idmap') or load_csv(
            path.join(meta_path, 'work-id', '%s.csv' % canon_code))
        vol_no = [m[1] for m in id_map if m[0] == work_id]
        assert vol_no

        m = re.search(r'^\(.+\).{10,90}[編錄](\s|$)', author)
        if m:
            m = m.group().strip()
            author = '．'.join(m.split('．')[:3]) + ' 等' + m[-1]
        author = '\u3000'.join(re.sub('（.+）$', '', author).split('\u3000')[:4])

        title = re.sub(r'(——|（).+$', '', title)
        items.append([work_id, title,
                      canon_names[canon_code], category,
                      '..'.join([re.sub('^[A-Z]+0*', '', n) for n in vol_no[0].split('..')]),
                      extent + '卷', author, time])
    save_csv(items, 'work.csv')


if __name__ == '__main__':
    build_meta()
