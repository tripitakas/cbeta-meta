#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
import sys
import csv
import json
import re

meta_path = '../cbeta-metadata'
cache = {}

# CBETA藏经代码
canon_names = {
    'A': '趙城金藏',
    'B': '補編',
    'C': '中華藏',
    'D': '國圖',
    'F': '房山石經',
    'G': '佛教大藏經',
    'GA': '佛寺志彙',
    'GB': '佛寺志叢',
    'I': '北朝佛拓',
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
    'X': '卍新續藏',
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
        with open(filename, 'w') as f:
            c = csv.writer(f)
            c.writerows(rows)
            return True
    except IOError as e:
        sys.stderr.write('Fail to save %s: %s\n' % (filename, str(e)))


def build_meta():
    all_title_file = path.join(meta_path, 'titles', 'all-title-byline.csv')
    titles = load_csv(all_title_file)[1:]
    items = ['经号,经名,所属藏经,部类,册别,卷数,字数,作译者,时间'.split(',')]

    # work_id: 从XML文件名提取的典籍編號，例如从 GA009n0008 取首末部分得到 GA0008
    # see get_work_id_from_file_basename in https://github.com/RayCHOU/ruby-cbeta/blob/master/lib/cbeta.rb
    for work_id, title, extent, author in titles:  # 典籍編號,典籍名稱,卷數,作譯者
        canon_code = re.search('^([A-Z]{1,2})', work_id).group()  # 藏经编码，一或二个大写字母
        if canon_code not in canon_names and len(canon_code) > 1:
            canon_code = canon_code[:-1]  # 例如 J01nA042->JA->J

        title = re.sub(r'(——|（).+$', '', title)
        if len(title) > 30:
            continue

        times = cache[canon_code + '_time'] = cache.get(canon_code + '_time') or load_json(
            path.join(meta_path, 'time', 'out', '%s.json' % canon_code))
        assert times
        times, dynasty = times.get(work_id, {}), ''
        dn = times.get('dynasty')
        if dn and dn != author and dn not in ['失譯', '日本', '朝鮮'] and (
                        len(dn) < 3 or not re.search('[造糅譯集述釋頌論說著錄編圖註寫撰譯作製本英薩詩]$|[(（]', dn)):
            if times.get('time_from'):
                dn += '%s~%s' % (times['time_from'], times['time_to'])
            dynasty = dn

        categories = cache[canon_code + '_category'] = cache.get(canon_code + '_category') or load_json(
            path.join(meta_path, 'category', 'work_categories.json'))
        assert categories
        category = categories.get(work_id, {}).get('category_names', '')

        char_count = cache[canon_code + '_char_count'] = cache.get(canon_code + '_char_count') or load_csv(
            path.join(meta_path, 'char-count', 'without-puncs', '%s.csv' % canon_code))
        char_count2 = cache[canon_code + '_char_count2'] = cache.get(canon_code + '_char_count2') or load_csv(
            path.join(meta_path, 'char-count', 'without-puncs', '_%s.csv' % canon_code)) or []
        assert char_count
        char_count = [m[1] for m in char_count if m[0] == work_id] + [m[1] for m in char_count2 if m[0] == work_id]

        id_map = cache[canon_code + '_idmap'] = cache.get(canon_code + '_idmap') or load_csv(
            path.join(meta_path, 'work-id', '%s.csv' % canon_code))
        vol_no = [m[1] for m in id_map if m[0] == work_id]
        assert vol_no

        m = re.search(r'^\(.+\).{10,90}[編錄](\s|$)', author)
        if m:
            m = m.group().strip()
            author = '．'.join(m.split('．')[:3]) + ' 等' + m[-1]
        author = '\u3000'.join(re.sub('（.+）$', '', author).split('\u3000')[:4])

        items.append([work_id, title,
                      canon_names[canon_code], category,
                      '..'.join([re.sub('^[A-Z]+', '', n) for n in vol_no[0].split('..')]),
                      int(extent), char_count and int(char_count[0]) or 0, author, dynasty])
    save_csv(items, 'work.csv')


if __name__ == '__main__':
    build_meta()
