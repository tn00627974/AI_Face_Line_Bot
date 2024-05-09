import pymysql, json, configparser
config = configparser.ConfigParser()
config.read('config.ini')

host = config.get('mysql', 'host')
port = int(config.get('mysql', 'port'))
user = config.get('mysql', 'user')
passwd = config.get('mysql', 'passwd')
db = config.get('mysql', 'db')
charset = config.get('mysql', 'charset')
end_point = config.get('line-bot', 'end_point')

# 商品資料
mark = {
        0: "FOAM", 1: "上山採藥", 2: "肌研", 3: "肌研", 4: "肌研",
        5: "莎娜", 6: "露姬婷", 7: "清妍", 8: "專科", 9: "高絲",
        10: "Biore", 11: "Biore", 12: "Bifesta", 13: "Biore", 14: "露姬婷",
        15: "Bifesta", 16: "Bifesta", 17: "Bifesta"
}

# 商品網址
urls = {
    0: 'https://www.cosme.net.tw/products/87330/reviews',
    1: 'https://www.cosme.net.tw/products/4989/reviews',
    2: 'https://www.cosme.net.tw/products/85513/reviews',
    3: 'https://www.cosme.net.tw/products/79415/reviews',
    4: 'https://www.cosme.net.tw/products/40527/reviews',
    5: 'https://www.cosme.net.tw/products/19398/reviews',
    6: 'https://www.cosme.net.tw/products/79637/reviews',
    7: 'https://www.cosme.net.tw/products/90191/reviews',
    8: 'https://www.cosme.net.tw/products/105363/reviews',
    9: 'https://www.cosme.net.tw/products/57958/reviews',
    10: 'https://www.cosme.net.tw/products/67787/reviews',
    11: 'https://www.cosme.net.tw/products/58118/reviews',
    12: 'https://www.cosme.net.tw/products/89784/reviews',
    13: 'https://www.cosme.net.tw/products/67788/reviews',
    14: 'https://www.cosme.net.tw/products/36729/reviews',
    15: 'https://www.cosme.net.tw/products/82073/reviews',
    16: 'https://www.cosme.net.tw/products/82072/reviews',
    17: 'https://www.cosme.net.tw/products/82074/reviews'
}

# 商品圖片
imgs = {
    0: "https://imgur.com/ojqgngi.jpg",
    1: "https://imgur.com/tlAiF6h.jpg",
    2: "https://imgur.com/GMueS4b.jpg",
    3: "https://imgur.com/N9Omj8j.jpg",
    4: "https://imgur.com/jYEZal6.jpg",
    5: "https://imgur.com/OmgeQOn.jpg",
    6: "https://imgur.com/JLAYFzr.jpg",
    7: "https://imgur.com/q3mgxPe.jpg",
    8: "https://imgur.com/iTWuoIU.jpg",
    9: "https://imgur.com/jzy7shE.jpg",
    10: "https://imgur.com/y95d5Rb.jpg",
    11: "https://imgur.com/KMt0vV0.jpg",
    12: "https://imgur.com/z63oxxf.jpg",
    13: "https://imgur.com/U86lFJk.jpg",
    14: "https://imgur.com/PIFIWCL.jpg",
    15: "https://imgur.com/3s8yCHu.jpg",
    16: "https://imgur.com/BjcObqE.jpg",
    17: "https://imgur.com/hvUIe6p.jpg"
}

# select_1 功能 : 查詢 items_table 資料(0~17) 18種商品
def select_1(product_id):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    print('Successfully connected!')
    cursor = conn.cursor()

    sql = f"""
    select ID, 簡稱, 平均分數, 效果, 優點, 缺點, 推薦1, 推薦2, 推薦3 from items_table
    where ID = {product_id};
    """
    cursor.execute(sql)
    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return data

 
# select_2 功能 : 查詢 items_table 對應膚質與年齡分類 回傳給使用者建立訊息

def select_2(product_id, age_type):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    print('Successfully connected!')
    cursor = conn.cursor()

    """
    A1: 乾性肌膚 20歲以下
    A2: 乾性肌膚 21-30歲
    A3: 乾性肌膚 31-45歲
    A4: 乾性肌膚 46歲以上
    B1: 油性肌膚 20歲以下
    B2: 油性肌膚 21-30歲
    B3: 油性肌膚 31-45歲
    B4: 油性肌膚 46歲以上
    C1: 敏感性肌膚 20歲以下
    C2: 敏感性肌膚 21-30歲
    C3: 敏感性肌膚 31-45歲
    C4: 敏感性肌膚 46歲以上
    D1: 混合性肌膚 20歲以下
    D2: 混合性肌膚 21-30歲
    D3: 混合性肌膚 31-45歲
    D4: 混合性肌膚 46歲以上
    """
    
    sql = f"""
    select {age_type}分數, {age_type}效果 from items_table 
    where ID = {product_id};
    """
    cursor.execute(sql)
    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return data

b = {"A": "乾性肌膚", "2": "21-30歲"}
age_type = f"{list(b.keys())[0]}{list(b.keys())[1]}"
print(select_2(0,age_type))


def stars_1(js, math):
    star = {
    "type": "icon",
    "size": "lg",
    "url": "https://imgur.com/ZCwfMp0.png" # 滿星
    }

    starhelf = {
        "type": "icon",
        "size": "lg",
        "url": "https://imgur.com/eIiB8Qn.png" # 半星
    }

    starlast = {
        "type": "text",
        "text": f"{math}",
        "size": "sm",
        "margin": "md",
        "color": "#111111",
        "offsetTop": "none",
        "offsetBottom": "none",
        "offsetStart": "none",
        "offsetEnd": "none"
    }

    for i in range(int(math)):
        js["body"]["contents"][2]["contents"].append(star)

    num = int(math * 10 % 10)
    if num >= 7 and num <= 9:
        js["body"]["contents"][2]["contents"].append(star)
        js["body"]["contents"][2]["contents"].append(starlast)
    elif num >= 4 and num <= 6:
        js["body"]["contents"][2]["contents"].append(starhelf)
        js["body"]["contents"][2]["contents"].append(starlast)
    else:
        js["body"]["contents"][2]["contents"].append(starlast)

    return js


def stars_2(js, math, info_number):
    star = {
    "type": "icon",
    "size": "lg",
    "url": "https://imgur.com/ZCwfMp0.png"
    }

    starhelf = {
        "type": "icon",
        "size": "lg",
        "url": "https://imgur.com/eIiB8Qn.png"
    }

    starlast = {
        "type": "text",
        "text": f"{math}",
        "size": "sm",
        "margin": "md",
        "color": "#111111",
        "offsetTop": "none",
        "offsetBottom": "none",
        "offsetStart": "none",
        "offsetEnd": "none"
    }

    for i in range(int(math)):
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(star)

    num = int(math * 10 % 10)
    if num >= 7 and num <= 9:
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(star)
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(starlast)
    elif num >= 4 and num <= 6:
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(starhelf)
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(starlast)
    else:
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(starlast)

    return js

# 顯示商品資訊
def load_js1(data): # select ID, 簡稱, 平均分數, 效果, 優點, 缺點, 推薦1, 推薦2, 推薦3 from items_table
    with open('v1.json', mode='r', encoding='utf-8') as fi:
        js = json.load(fi)

    math = data[2]
    js = stars_1(js, math)

    js["body"]["contents"][0]["text"] = mark[data[0]]  # 品牌
    js['body']['contents'][1]['text'] = data[1]  # 商品名稱
    js['body']['contents'][3]['contents'][0]['contents'][1]['text'] = data[3]  # 效果
    js['body']['contents'][3]['contents'][1]['contents'][1]['text'] = data[4] # 優點
    js["body"]["contents"][3]["contents"][1]["contents"][2]["contents"][1]["text"] = data[5] # 缺點
    js['footer']['contents'][1]['action']['text'] = f"推薦:{data[1]}"  # 推薦商品
    js['hero']['url'] = imgs[data[0]]  # 圖片
    js['footer']['contents'][0]['action']['uri'] = urls[data[0]]  # 網址
    
    return js

# 顯示商品資訊
def load_js2(data):
    with open('v2.json', mode='r', encoding='utf-8') as fi:
        js = json.load(fi)

    for info_number in range(3):
        math = data[info_number][2]
        js = stars_2(js, math, info_number)

        js['contents'][info_number]["body"]["contents"][0]["text"] = mark[data[info_number][0]]  # 品牌
        js['contents'][info_number]['body']['contents'][1]['text'] = data[info_number][1]  # 商品名稱
        js['contents'][info_number]['body']['contents'][3]['contents'][0]['contents'][1]['text'] = data[info_number][3]  # 效果
        js['contents'][info_number]['body']['contents'][3]['contents'][1]['contents'][1]['text'] = data[info_number][4] # 優點
        js['contents'][info_number]["body"]["contents"][3]["contents"][1]["contents"][2]["contents"][1]["text"] = data[info_number][5] # 缺點
        js['contents'][info_number]['footer']['contents'][1]['action']['text'] = f"推薦:{data[info_number][1]}"  # 推薦商品
        js['contents'][info_number]['hero']['url'] = imgs[data[info_number][0]]  # 圖片
        js['contents'][info_number]['footer']['contents'][0]['action']['uri'] = urls[data[info_number][0]]  # 網址
    
    return js

# 推薦商品
def push_db(id_tp):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    print('Successfully connected!')
    cursor = conn.cursor()

    sql = f"""
    select ID, 簡稱, 平均分數, 效果, 優點, 缺點, 推薦1, 推薦2, 推薦3 from items_table
    where ID = {id_tp[0]} or ID = {id_tp[1]} or ID = {id_tp[2]};
    """
    cursor.execute(sql)
    data = cursor.fetchall()

    info = []
    for i in id_tp:
        for x in range(3):
            if data[x][0] == i:
                info.append((data[x]))  # 調整排序問題

    cursor.close()
    conn.close()

    return info
