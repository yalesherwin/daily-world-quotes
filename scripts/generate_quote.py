#!/usr/bin/env python3
import os, json, hashlib, random, datetime, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'docs', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

TODAY_FILE = os.path.join(DATA_DIR, 'today.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')
USED_FILE = os.path.join(DATA_DIR, 'used_ids.json')

QUOTE_SOURCE = 'https://type.fit/api/quotes'


def http_get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8', errors='ignore'))


def translate_en_to_zh(text):
    # 免费翻译接口，失败则返回原文
    try:
        q = urllib.parse.quote(text)
        url = f'https://api.mymemory.translated.net/get?q={q}&langpair=en|zh-CN'
        data = http_get_json(url, timeout=20)
        zh = data.get('responseData', {}).get('translatedText', '').strip()
        return zh if zh else text
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


def pick_quote(quotes, used):
    pool = []
    for q in quotes:
        text = normalize(q.get('text', ''))
        if len(text) < 18:
            continue
        author = normalize(q.get('author') or 'Unknown')
        qid = quote_id(text, author)
        if qid not in used:
            pool.append((qid, text, author))

    if not pool:
        used.clear()
        return pick_quote(quotes, used)

    return random.choice(pool)


def main():
    today = datetime.date.today().isoformat()
    used = set(load_json(USED_FILE, []))
    history = load_json(HISTORY_FILE, [])

    quotes = http_get_json(QUOTE_SOURCE)
    qid, en, author = pick_quote(quotes, used)
    zh = translate_en_to_zh(en)

    item = {
        'id': qid,
        'date': today,
        'author': author,
        'quote_en': en,
        'quote_zh': zh,
        'source': 'https://type.fit/api/quotes'
    }

    save_json(TODAY_FILE, item)

    history = [h for h in history if h.get('id') != qid]
    history.insert(0, item)
    history = history[:180]
    save_json(HISTORY_FILE, history)

    used.add(qid)
    save_json(USED_FILE, sorted(list(used)))

    print('Generated:', item)


if __name__ == '__main__':
    main()
