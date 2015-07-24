#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division


import unicodedata as unidata
# import ujson as json
# import simplejson as json
import json

import collections


JIS_NAME = dict({
  'KATAKANA LETTER HA': 'ハ',
  'KATAKANA LETTER HE': 'ヘ',
  'KATAKANA LETTER I': 'イ',
  'KATAKANA LETTER TI': 'チ',
  'KATAKANA LETTER YU': 'ユ',
  'KATAKANA LETTER TO': 'ト',
  'KATAKANA LETTER SE': 'セ',
  'KATAKANA LETTER ZI': 'ジ',
  'KATAKANA LETTER YA': 'ヤ',
  'KATAKANA LETTER TO': 'ト',
  'HIRAGANA DIGRAPH YORI': 'より',
  'HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK': '°',
  'HALFWIDTH KATAKANA LETTER NI': 'ニ',
  'HALFWIDTH KATAKANA LETTER NU': 'ヌ',
  'HALFWIDTH KATAKANA LETTER SO': 'ソ',
  'HALFWIDTH KATAKANA LETTER RU': 'ル',
  'HALFWIDTH KATAKANA LETTER TU': 'ツ',
  'HALFWIDTH KATAKANA LETTER TE': 'テ',
  'HALFWIDTH KATAKANA LETTER MO': 'モ',
  'HALFWIDTH KATAKANA LETTER YA': 'ヤ',
  'HALFWIDTH KATAKANA LETTER YU': 'ユ',
  'HALFWIDTH KATAKANA LETTER YO': 'ヨ',
  'HALFWIDTH KATAKANA LETTER RE': 'レ',
  'HALFWIDTH KATAKANA LETTER RO': 'ロ',
  'HALFWIDTH KATAKANA LETTER WA': 'ワ',

})

JIS_HIRAGANA = collections.OrderedDict({

})

JIS_KATAKANA = collections.OrderedDict({

})

JIS_KANJI = collections.OrderedDict({

})

JIS_KATAKANA_F = collections.OrderedDict({

})

JIS_KATAKANA_H = collections.OrderedDict({

})

JIS_KATAKANA_H2F = collections.OrderedDict({

})

JIS_HIRAGANA_S2L = collections.OrderedDict({

})


# HIRAGANA          : [0x3040 : 0x309f]
# KATAKANA          : [0x30a0 : 0x30ff]
# KANJI             : [0x4e00 : 0x9faf]
# HALFWIDTH KATAKANA: [0xff65 : 0xff9f]

print('HIRAGANA TABLE...')
for i in xrange(0x3040, 0x309f+1):
  try:
    name = unidata.name(unichr(i))
    JIS_HIRAGANA[u'\\u%4x %s' % (i, name)] = u'%s' % unichr(i)
  except:
    pass

print('KATAKANA TABLE...')
for i in xrange(0x30a0, 0x30ff+1):
  try:
    name = unidata.name(unichr(i))
    JIS_KATAKANA[u'\\u%4x %s' % (i, name)] = u'%s' % unichr(i)
    romaji = name.split()[-1]
    JIS_KATAKANA_F[romaji] = u'%s, \\u%4x' % (unichr(i), i)
  except:
    pass

print('KANJI TABLE...')
for i in xrange(0x4e00, 0x9faf+1):
  try:
    name = unidata.name(unichr(i))
    JIS_KANJI[u'\\u%4x %s' % (i, name)] = u'%s' % unichr(i)
  except:
    pass

print('HHALFWIDTH KATAKANA TABLE...')
for i in xrange(0xff65, 0xff9f+1):
  try:
    name = unidata.name(unichr(i))
    romaji = name.split()[-1]
    JIS_KATAKANA_H[romaji] = u'%s, \\u%4x' % (unichr(i), i)
    if romaji in JIS_KATAKANA_F:
      JIS_KATAKANA_H2F[unichr(i)] = u'%s' % (JIS_KATAKANA_F[romaji].split(',')[0].strip())
    else:
      JIS_KATAKANA_H2F[unichr(i)] = u'%s' % ('----------')
  except:
    pass
JIS_KATAKANA_H2F['DOT'] = u'\u00b7'
JIS_KATAKANA_H2F['HYPHEN'] = u'='


def saveTable():
  # print dir(json)
  with open('jis_kanji.json', 'wt') as f:
    json.dump(JIS_KANJI, f, indent=2, ensure_ascii=False, encoding='utf-8')
  with open('jis_hiragana.json', 'wt') as f:
    json.dump(JIS_HIRAGANA, f, indent=2, ensure_ascii=False, encoding='utf-8')
  with open('jis_katakana.json', 'wt') as f:
    json.dump(JIS_KATAKANA, f, indent=2, ensure_ascii=False, encoding='utf-8')
  with open('jis_katakana_f.json', 'wt') as f:
    json.dump(JIS_KATAKANA_F, f, indent=2, ensure_ascii=False, encoding='utf-8')
  with open('jis_katakana_h.json', 'wt') as f:
    json.dump(JIS_KATAKANA_H, f, indent=2, ensure_ascii=False, encoding='utf-8')
  with open('jis_katakana_h2f.json', 'wt') as f:
    json.dump(JIS_KATAKANA_H2F, f, indent=2, ensure_ascii=False, encoding='utf-8')

def katakana_h2f():
  pass

if __name__ == '__main__':
  saveTable()
  # print json.dumps(JIS_KATAKANA_F, indent=2, ensure_ascii=False, encoding='utf-8')
  # print json.dumps(JIS_KATAKANA_H, indent=2, ensure_ascii=False, encoding='utf-8')
  # print json.dumps(JIS_KATAKANA_H2F, indent=2, ensure_ascii=False, encoding='utf-8')
