#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
from glob2 import glob
import os.path as path
from lxml import etree

XML_P5_DIR = '/Users/xiandu/Develop/xml-p5'
MULU_DIR = '/Users/xiandu/Develop/cbeta-mulu'
JUAN_DIR = '/Users/xiandu/Develop/cbeta-juan'


def extract_mulu_from_xml_p5():
    """ 从CBETA xml-p5中提取目录信息 """
    for fn in glob(path.join(XML_P5_DIR, '**', '*.xml')):
        print('processing ' + fn)
        root = etree.parse(fn)
        namespaces = {'cb': 'http://www.cbeta.org/ns/1.0'}
        # 获取id
        id = path.basename(fn).split('.')[0]
        # 获取目录
        mulu = []
        for item in root.xpath('//cb:mulu', namespaces=namespaces):
            if item.xpath('@type') == ['卷']:
                continue
            # 获取行首
            lb_items = item.xpath('./preceding::*[@ed]')
            lb = lb_items[-1].xpath('@n') if lb_items else []
            mulu.append({
                'level': ','.join(item.xpath('@level')),
                'n': ','.join(item.xpath('@n')),
                'type': ','.join(item.xpath('@type')),
                'text': ','.join(item.xpath('text()')),
                'head': id + '_' + ','.join(lb)
            })

        # 写文件
        head = re.search(r'^([A-Z]{1,2})(\d+)n(.*)', path.basename(fn))
        assert head and head.group()
        to_dir = path.join(MULU_DIR, head.group(1), head.group(1) + head.group(2))
        if not path.exists(to_dir):
            os.makedirs(to_dir)
        with open(path.join(to_dir, path.splitext(path.basename(fn))[0] + '.json'), 'w') as fp:
            if mulu:
                json.dump(mulu, fp, ensure_ascii=False)
            else:
                fp.write('')
    print('finished!')


def extract_juan_from_xml_p5():
    """ 从CBETA xml-p5中提取卷信息 """
    for fn in glob(path.join(XML_P5_DIR, '**', '*.xml')):
        print('processing ' + fn)
        root = etree.parse(fn)
        namespaces = {'cb': 'http://www.cbeta.org/ns/1.0'}
        # 获取id
        id = path.basename(fn).split('.')[0]
        # 获取目录
        juan = []
        for item in root.xpath('//cb:juan', namespaces=namespaces):
            # 获取行首
            lb_items = item.xpath('./preceding::*[@ed]')
            lb = lb_items[-1].xpath('@n') if lb_items else []
            juan.append({
                'n': ','.join(item.xpath('@n')),
                'fun': ','.join(item.xpath('@fun')),
                'head': id + '_' + ','.join(lb)
            })

        # 写文件
        head = re.search(r'^([A-Z]{1,2})(\d+)n(.*)', path.basename(fn))
        assert head and head.group()
        to_dir = path.join(JUAN_DIR, head.group(1), head.group(1) + head.group(2))
        if not path.exists(to_dir):
            os.makedirs(to_dir)
        with open(path.join(to_dir, path.splitext(path.basename(fn))[0] + '.json'), 'w') as fp:
            if juan:
                json.dump(juan, fp, ensure_ascii=False)
            else:
                fp.write('')
    print('finished!')


if __name__ == '__main__':
    extract_mulu_from_xml_p5()
