# -*- coding: utf-8 -*-
from os import makedirs
from os.path import abspath, dirname, join

import yaml
from 轉到臺灣言語資料庫.整理詞目總檔 import 整理詞目總檔
from 轉到臺灣言語資料庫.整理又音 import 整理又音
from 轉到臺灣言語資料庫.整理方言詞 import 整理方言詞
from 轉到臺灣言語資料庫.整理外來詞 import 整理外來詞
from 轉到臺灣言語資料庫.整理例句 import 整理例句


class 整合到資料庫:
    教育部閩南語辭典 = {'名': '教育部閩南語辭典'}
    薛丞宏 = {'名': '薛丞宏'}
    公家內容 = {
        '版權': '姓名標示-禁止改作 3.0 台灣',
        '語言腔口': '閩南語',
        '著作所在地': '臺灣',
        '著作年': '2015',
    }

    def 處理詞條(self):
        華語詞條資料 = {}
        全部下層陣列 = []
        for 整合 in [
            整理詞目總檔(),
            整理又音(),
            整理方言詞(),
            整理外來詞(),
            整理例句(),
        ]:
            for _第幾个, 詞條 in enumerate(整合.得著詞條()):
                臺語詞條 = self._揣出臺語詞條(詞條)
                try:
                    for 華語文本 in 詞條['華語']:
                        華語內容 = (詞條['種類'], 華語文本,)
                        if 華語內容 not in 華語詞條資料:
                            華語詞條資料[華語內容] = []
                        華語詞條資料[華語內容].append(臺語詞條)
                except KeyError:
                    全部下層陣列.append(臺語詞條)
        for 華語, 下層資料 in sorted(華語詞條資料.items()):
            華語種類, 華語文本 = 華語
            華語內容 = {
                '來源': self.教育部閩南語辭典,
                '種類': 華語種類,
                '外語語言': '華語',
                '外語資料': 華語文本,
                '下層': 下層資料,
            }
            全部下層陣列.append(華語內容)
        全部資料 = {'下層': 全部下層陣列}
        全部資料.update(self.公家內容)
        return 全部資料

    def _揣出臺語詞條(self, 詞條):
        臺語內容 = {
            '來源': self.教育部閩南語辭典,
            '種類': 詞條['種類'],
            '文本資料': 詞條['文本資料'],
            '下層': [],
        }
        try:
            臺語內容['屬性'] = 詞條['屬性']
        except:
            pass
        try:
            for 漢字, 音標 in 詞條['校對']:
                校對內容 = {
                    '來源': self.薛丞宏,
                    '種類': 詞條['種類'],
                    '文本資料': 漢字,
                }
                if 音標:
                    校對內容['屬性'] = {'音標': 音標}
                臺語內容['下層'].append(校對內容)
        except KeyError:
            臺語內容.pop('下層')
        return 臺語內容


if __name__ == '__main__':
    makedirs(join(dirname(abspath(__file__)), '資料'), exist_ok=True)
    全部資料 = 整合到資料庫().處理詞條()
    with open(join(dirname(abspath(__file__)), '資料', 'xls整理.yaml'), 'w') as 檔案:
        yaml.dump(全部資料, 檔案, default_flow_style=False, allow_unicode=True)
