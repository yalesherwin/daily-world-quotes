#!/usr/bin/env python3
import os, json, hashlib, datetime, urllib.request, urllib.parse, random, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'docs', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

TODAY_FILE = os.path.join(DATA_DIR, 'today.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')
USED_FILE = os.path.join(DATA_DIR, 'used_ids.json')

CN_SOURCE = 'https://v1.hitokoto.cn/?encode=json&max_length=90'


def http_get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8', errors='ignore'))


def translate_zh_to_en(text):
    # 免费翻译接口；失败则返回中文原文
    try:
        q = urllib.parse.quote(text)
        url = f'https://api.mymemory.translated.net/get?q={q}&langpair=zh-CN|en'
        data = http_get_json(url, timeout=20)
        en = data.get('responseData', {}).get('translatedText', '').strip()
        return en if en else text
    except Exception:
        return text


def normalize(s):
    return ' '.join((s or '').strip().split())


def quote_id(text, author):
    raw = f"{normalize(text)}|{normalize(author)}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_new_cn_quote(used, max_try=50):
    for _ in range(max_try):
        d = http_get_json(CN_SOURCE)
        zh = normalize(d.get('hitokoto', ''))
        if len(zh) < 8:
            continue
        author = normalize(d.get('from_who') or d.get('from') or '佚名')
        qid = quote_id(zh, author)
        if qid in used:
            time.sleep(0.2)
            continue
        en = translate_zh_to_en(zh)
        return {
            'id': qid,
            'author': author,
            'quote_zh': zh,
            'quote_en': en,
            'source': 'https://v1.hitokoto.cn/'
        }
    raise RuntimeError('No new quote found after retries')


def main():
    today = datetime.date.today().isoformat()
    used = set(load_json(USED_FILE, []))
    history = load_json(HISTORY_FILE, [])

    item = fetch_new_cn_quote(used)
    item['date'] = today

    save_json(TODAY_FILE, item)

    history = [h for h in history if h.get('id') != item['id']]
    history.insert(0, item)
    history = history[:365]
    save_json(HISTORY_FILE, history)

    used.add(item['id'])
    save_json(USED_FILE, sorted(list(used)))

    print('Generated:', item)


if __name__ == '__main__':
    main()
