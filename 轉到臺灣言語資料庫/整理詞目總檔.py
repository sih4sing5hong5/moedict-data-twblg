# -*- coding: utf-8 -*-
from 臺灣言語工具.解析整理.文章粗胚 import 文章粗胚
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.解析整理.轉物件音家私 import 轉物件音家私
from 臺灣言語工具.解析整理.物件譀鏡 import 物件譀鏡
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音 import 臺灣閩南語羅馬字拼音
from csv import DictReader
from os.path import join, abspath, dirname
import re
from sys import stderr


# from 臺灣言語資料庫.資料模型 import 來源表
# from 臺灣言語資料庫.資料模型 import 版權表
# from 臺灣言語資料庫.資料模型 import 種類表
from 臺灣言語資料庫.欄位資訊 import 字詞
from 臺灣言語資料庫.欄位資訊 import 語句


class 整理詞目總檔():
    例句會當變動符號 = False
    教育部閩南語辭典空白符號 = '\u3000 \t'
    詞目是音標 = re.compile('[a-z0-9 ]')

    def __init__(self):
        self._粗胚 = 文章粗胚()
        self._分析器 = 拆文分析器()
        self._轉音家私 = 轉物件音家私()
        self._譀鏡 = 物件譀鏡()

    def 得著詞條(self):
        對應表 = self.編號對應華語()
        with open(join(dirname(abspath(__file__)), '..', 'uni', '詞目總檔.csv')) as 檔:
            讀檔 = DictReader(檔)
            for row in 讀檔:
                row.pop('文白')
                row.pop('部首')
                for 詞條 in self.詞目總檔(**row):
                    try:
                        結果 = self.正規化詞條音標(詞條)
                        if 結果:
                            try:
                                結果['華語'] = 對應表[結果['主編碼']]
                            except:
                                pass
                            yield 結果
                    except Exception as 錯誤:
                        print(錯誤, 詞條, file=stderr)

    def 正規化詞條音標(self, 詞條):
        try:
            音標 = 詞條['屬性']['音標']
        except:
            if self.詞目是音標.match(詞條['文本資料']):
                if int(詞條['主編碼']) > 31000 and int(詞條['主編碼']) < 32000:
                    return  # 予外來語來做
                else:
                    raise RuntimeError('有音標組成的資料！？')
            return 詞條
        漢字 = 詞條['文本資料']
        處理減號音標 = self._粗胚.建立物件語句前處理減號(臺灣閩南語羅馬字拼音, 音標)
        處理了音標 = self._粗胚.符號邊仔加空白(處理減號音標)

        try:
            原音章物件 = self._分析器.產生對齊章(漢字, 處理了音標)
            上尾章物件 = self._轉音家私.轉音(臺灣閩南語羅馬字拼音, 原音章物件)
            詞條['屬性']['音標'] = self._譀鏡.看音(上尾章物件)
            漢字 = 詞條['文本資料'] = self._譀鏡.看型(上尾章物件)
            return 詞條
        except:
            暫時詞條 = {}
            暫時詞條.update(詞條)
            暫時詞條.pop('主編碼')
            詞條['校對'] = []
            for 結果詞條 in self.正規化詞條音標特別處理(暫時詞條):
                詞條['校對'].append((結果詞條['文本資料'], 結果詞條['屬性']['音標']))
            return 詞條

    def 正規化詞條音標特別處理(self, 詞條):
        音標 = 詞條['屬性']['音標']
        漢字 = 詞條['文本資料']
        華語地名 = {
            ('竹圍', 'Tik-uî-á'): '竹圍仔',
            ('石牌', 'Tsio̍h-pâi-á'): '石牌仔',
            ('拔林', 'Pa̍t-á-nâ'): '拔仔林',
            ('圓山', 'Înn-suann-á'): '圓山仔',
            ('三重', 'Sann-tîng-poo'): '三重埔',
        }
        漢字漏勾 = {
            (
                '收瀾收予焦，予你生一个有',
                'Siu-nuā siu hōo ta, hōo lí senn tsi̍t ê ū lān-pha.'
            ): '收瀾收予焦，予你生一个有𡳞脬。'
        }
        雙地名 = {
            ('苓仔寮、能雅寮', 'Lîng-á-liâu'),
        }
        括號雙地名 = {
            ('竿(菅)蓁林', 'Kuann-tsin-nâ'),
        }
        雙音標 = {
            ('汐止', 'Si̍k-tsí(Si̍p-tsí)'),
        }
        毋是漢語的音標 = {  # 講毋是漢語，無愛變ian
            ('屏遮那', 'Hè-sen-ná'):
            'Hè-sian-ná'
        }
        漢字錯誤 = {}
        漢字錯誤.update(華語地名)
        漢字錯誤.update(漢字漏勾)
        if (漢字, 音標) in 漢字錯誤:
            詞條['文本資料'] = 漢字錯誤[(漢字, 音標)]
            return [self.正規化詞條音標(詞條)]
        elif (漢字, 音標) in 雙地名:
            第一個詞條, 第二個詞條 = {}, {}
            第一個詞條.update(詞條)
            第二個詞條.update(詞條)
            第一個詞條['文本資料'], 第二個詞條['文本資料'] = 漢字.split('、')
            return [
                self.正規化詞條音標(第一個詞條),
                self.正規化詞條音標(第二個詞條)
            ]
        elif (漢字, 音標) in 括號雙地名:
            第一個詞條, 第二個詞條 = {}, {}
            第一個詞條.update(詞條)
            第二個詞條.update(詞條)
            拆漢字 = re.match('(.+)\((.+)\)(.+)', 漢字)
            第一個詞條['文本資料'] = 拆漢字.group(1) + 拆漢字.group(3)
            第二個詞條['文本資料'] = 拆漢字.group(2) + 拆漢字.group(3)
            return [
                self.正規化詞條音標(第一個詞條),
                self.正規化詞條音標(第二個詞條)
            ]
        elif (漢字, 音標) in 雙音標:
            第一個詞條, 第二個詞條 = {}, {}
            第一個詞條.update(詞條)
            第二個詞條.update(詞條)
            拆音標 = re.match('(.+)\((.+)\)', 音標)
            第一個詞條['屬性']['音標'], 第二個詞條['屬性']['音標'] = 拆音標.group(1, 2)
            return [
                self.正規化詞條音標(第一個詞條),
                self.正規化詞條音標(第二個詞條)
            ]
        elif (漢字, 音標) in 毋是漢語的音標:
            詞條['屬性']['音標'] = 毋是漢語的音標[(漢字, 音標)]
            return [self.正規化詞條音標(詞條)]
        else:
            raise

    def 詞目總檔(self, 主編碼, 屬性, 詞目, 音讀):
        用假名的音標 = {
            ('那卡西', 'ながし'):
            '1na1-1ka7-1si3'
        }
        if int(屬性) == 25:
            種類 = 語句
        else:
            種類 = 字詞
        if 音讀 is '':
            yield {
                '主編碼': 主編碼,
                '文本資料': 詞目,
                '種類': 種類,
            }
        elif (詞目, 音讀) in 用假名的音標:
            yield {
                '主編碼': 主編碼,
                '文本資料': 詞目,
                '種類': 種類,
                '校對': [(用假名的音標[(詞目, 音讀)], '')],
            }
            yield {
                '主編碼': 主編碼,
                '文本資料': 音讀,
                '種類': 種類,
                '校對': [(用假名的音標[(詞目, 音讀)], '')],
            }
        else:
            優勢音 = 音讀.split('/')
            if len(優勢音) == 1:
                yield {
                    '主編碼': 主編碼,
                    '文本資料': 詞目,
                    '種類': 種類,
                    '屬性': {'音標': 音讀},
                }
            elif len(優勢音) == 2:
                混合優勢音, 偏泉優勢音 = [
                    音.strip(self.教育部閩南語辭典空白符號)
                    for 音 in 優勢音]
                yield {
                    '主編碼': 主編碼,
                    '文本資料': 詞目,
                    '種類': 種類,
                    '屬性': {'音標': 混合優勢音, '腔口': '高雄優勢腔'},
                }
                yield {
                    '主編碼': 主編碼,
                    '文本資料': 詞目,
                    '種類': 種類,
                    '屬性': {'音標': 偏泉優勢音, '腔口': '臺北優勢腔'},
                }
            else:
                for 結果 in self.三區詞目總檔(主編碼, 種類, 詞目, 音讀):
                    yield 結果
                return

    def 三區詞目總檔(self, 主編碼, 種類, 詞目, 音讀):
        if (詞目, 音讀) == ('俞', 'Jû/Lû/Jî'):
            return [
                {
                    '主編碼': 主編碼,
                    '文本資料': 詞目,
                    '種類': 種類,
                    '屬性': {'音標': 'Jû', '腔口': '高雄優勢腔'},
                },
                {
                    '主編碼': 主編碼,
                    '文本資料': 詞目,
                    '種類': 種類,
                    '屬性': {'音標': 'Lû', '腔口': '高雄優勢腔'},
                },
                {
                    '主編碼': 主編碼,
                    '文本資料': 詞目,
                    '種類': 種類,
                    '屬性': {'音標': 'Jî', '腔口': '臺北優勢腔'},
                }]
        raise RuntimeError('音讀不只兩區：{}'.format(音讀))

    def 編號對應華語(self):
        對應表 = {}
        with open(join(dirname(abspath(__file__)), '..', 'uni', '對應華語.csv')) as 檔:
            讀檔 = DictReader(檔)
            for row in 讀檔:
                if row['n_no'] not in 對應表:
                    對應表[row['n_no']] = []
                對應表[row['n_no']].append(row['kokgi'])
        return 對應表
