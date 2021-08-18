import os, json

def tojson(brands):
    targets = ['aNueNue']
    for brand in brands:
        if brand in targets:
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

def getTags(goods):
    allTags = []
    for good in goods:
        folder = brand + '\\' + good + '\\'
        with open(folder + 'msg.json', 'r', encoding='utf-8') as f:
            details = json.load(f)
        for k in details.keys():
            if k not in allTags:
                allTags.append(k)
    with open('Tags.json', 'w', encoding='utf-8') as f:
        json.dump(allTags, f, ensure_ascii=False)
    return allTags

def getDetailTags(goods):
    tags = getTags(goods)
    res = {}
    ignored = ['价格', '品牌', '扬声器个数']
    for tag in tags:
        if tag in ignored:
            continue
        res[tag] = []
        for good in goods:
            folder = brand + '\\' + good + '\\'
            with open(folder + 'msg.json', 'r', encoding='utf-8') as f:
                details = json.load(f)
            if tag in details.keys():
                res[tag].append(details[tag])
    with open('DetailTags.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False)

brands = [o for o in os.listdir('.') if os.path.isdir(o)]
for brand in brands:
    goods = os.listdir(brand)
getDetailTags(goods)
# tojson(brands)
