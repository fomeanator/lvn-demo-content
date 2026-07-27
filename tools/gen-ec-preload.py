#!/usr/bin/env python3
# ПОЛНАЯ блокирующая предзагрузка EC: все ассеты игры пишутся в manifest.json
# каждой главе ec как chapter.assets с critical=true — клиент качает ВСЁ на
# экране загрузки (гейт Play), в игре ничего не догружается. Плюс дублирующий
# scripts/ec-preload.lvns (безвреден: к началу главы кэш уже полон).
# Запуск из корня контента:  python3 tools/gen-ec-preload.py
import json, re, itertools, os, glob, collections

urls = set()
for f in glob.glob('scripts/ec-ch0*.lvn'):
    d = json.load(open(f))
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ('sprite_url','url','body_url','clothes_url','hair_url','bg_url') \
                   and isinstance(v, str) and v.startswith('/content/'):
                    urls.add(v)
                else: walk(v)
        elif isinstance(o, list):
            for x in o: walk(x)
    walk(d)

m = json.load(open('manifest.json'), object_pairs_hook=collections.OrderedDict)
for k, v in m['sprites'].items():
    if not (k.startswith('ec_') or k.startswith('fx_')): continue
    axes = v.get('axes', {})
    for layer in v.get('layers', []):
        u = layer.get('url', '')
        ph = re.findall(r'\{(\w+)\}', u)
        if not ph: urls.add(u); continue
        for combo in itertools.product(*[axes.get(p, []) for p in ph]):
            uu = u
            for p, val in zip(ph, combo): uu = uu.replace('{'+p+'}', val)
            urls.add(uu)
for t in m.get('titles', []):
    for key in ('cover_url','bg_url'):
        if t.get(key): urls.add(t[key])

def disk(u): return u.removeprefix('/content/').split('?')[0]
missing = [u for u in sorted(urls) if not os.path.exists(disk(u))]
urls = {u for u in urls if u not in missing}

def kind(u): return 'audio' if u.endswith(('.ogg','.mp3','.wav')) else 'sprite'
def meta(u):
    sz = os.path.getsize(disk(u))
    return collections.OrderedDict([
        ("size", sz), ("kind", kind(u)),
        ("tier", "large" if sz > 1_000_000 else ("mini" if sz < 65_536 else "normal")),
        ("critical", True),
    ])
assets = collections.OrderedDict((u, meta(u)) for u in sorted(urls))

ec = next(t for t in m['titles'] if t.get('id') == 'ec')
for season in ec.get('seasons', []):
    for ch in season.get('chapters', []):
        ch['assets'] = assets
json.dump(m, open('manifest.json','w'), ensure_ascii=False, indent=2)

body = '\n'.join([
    '// ⚡ EC — дублирующий прелоад (сгенерировано tools/gen-ec-preload.py).',
    '// Главный механизм — chapter.assets (critical) в manifest.json: клиент',
    '// качает ВСЁ на экране загрузки. Этот файл — страховка для dev-путей.',
    '']) + '\n' + '\n'.join(f'preload url="{u}" kind={kind(u)}' for u in sorted(urls)) + '\n'
open('scripts/ec-preload.lvns','w').write(body)
tot = sum(a['size'] for a in assets.values())
print(f'ассетов: {len(assets)}, вес: {tot/1e6:.1f} МБ — все critical у всех глав ec')
if missing: print('битые (пропущены):', missing)
