import os, json, csv
from typing import KeysView

def tojson(brands):
    targets = ['aNueNue']
    for brand in brands:
        if brand not in targets:
            continue
        goods = os.listdir(brand)
        for good in goods:
            folder = brand + '\\' + good + '\\'
            with open(folder + 'msg.json', 'r', encoding='utf-8') as f:
                details = json.load(f)
            m = {}
            m['价格'] = details[0]
            for i in details[1:]:
                content = i.split(':')
                m[content[0].strip()] = content[1].strip()
            with open(folder + 'msg.json', 'w', encoding='utf-8') as f:
                json.dump(m, f, ensure_ascii=False)

def getTags(brands):
    allTags = []
    for brand in brands:
        goods = os.listdir(brand)
        for good in goods:
            folder = brand + '\\' + good + '\\'
            with open(folder + 'msg.json', 'r', encoding='utf-8') as f:
                details = json.load(f)
            for k in details.keys():
                if k not in allTags:
                    allTags.append(k)
    print("Tags: " + str(allTags))
    with open('tags.json', 'w', encoding='utf-8') as f:
        json.dump(allTags, f, ensure_ascii=False)
    return allTags

def getDetailTags(brands):
    tags = getTags(brands)
    res = {}
    choices = ['品牌', '面板材质', '品位', '卷弦器', '指板材质', '背侧板材质', '尺寸', '型号', '价格区间', '颜色', '产地', '材质', '重量']
    print("Analyzing tags: " + str(choices))
    for tag in tags:
        if tag not in choices:
            continue
        res[tag] = []
        for brand in brands:
            goods = os.listdir(brand)
            for good in goods:
                folder = brand + '\\' + good + '\\'
                with open(folder + 'msg.json', 'r', encoding='utf-8') as f:
                    details = json.load(f)
                if tag in details.keys():
                    if details[tag] not in res[tag]:
                        res[tag].append(details[tag])
    with open('detailTags.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False)

def tocsv(fileName):
    l = fileName.split('.')[0]
    with open(fileName, 'r', encoding='utf-8') as f:
        jf = json.load(f)
    with open(l + '.csv', 'w', encoding='utf-8-sig', newline='') as f:
        keys = jf.keys()
        values = jf.values()
        max = 0
        for value in values:
            if len(value) > max:
                max = len(value)
        writer = csv.writer(f)
        writer.writerow(keys)
        for i in range(max):
            t = []
            for value in values:
                try:
                    nv = value[i]
                    t.append(nv)
                except IndexError as e:
                    t.append(' ')
            writer.writerow(t)

brands = [o for o in os.listdir('.') if os.path.isdir(o)]
# print("Brands: " + str(brands))
# getDetailTags(brands)
# tojson(brands)
tocsv('detailTags.json')