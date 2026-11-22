#!/usr/bin/env python3
"""Rebuild dlc.json from packs/*/pack.json and the zips actually present in the single songs/ folder.

Usage:  python3 tools/build_index.py
- Songs listed in pack.json get available=true once their zip exists.
- Any extra *.zip you drop into songs/ that no pack lists goes into an automatic "Other songs" pack (title/artist/level read from its manifest.json).
- Jacket thumbnails for new zips are extracted if Pillow is installed (pip install pillow).
"""
import json, os, io, sys, zipfile, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, 'packs')
SONGS = os.path.join(ROOT, 'songs')
PRESENT = {f for f in os.listdir(SONGS) if f.lower().endswith('.zip')} if os.path.isdir(SONGS) else set()
try:
    from PIL import Image
except Exception:
    Image = None

def read_manifest(path):
    try:
        with zipfile.ZipFile(path) as z:
            names = {n.rsplit('/', 1)[-1]: n for n in z.namelist()}
            m = json.loads(z.read(names['manifest.json']).decode('utf8'))
            jk = z.read(names['jacket']) if 'jacket' in names else None
            return m, jk
    except Exception as e:
        print('  ! cannot read', path, e)
        return None, None

def save_jacket(data, out):
    if not (Image and data): return False
    try:
        im = Image.open(io.BytesIO(data)).convert('RGBA')
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
        bg.convert('RGB').resize((200, 200)).save(out, quality=85)
        return True
    except Exception as e:
        print('  ! jacket failed', e); return False

order = json.load(open(os.path.join(PACKS, 'order.json')))['order']
for d in sorted(os.listdir(PACKS)):                      # new folders not in order.json go last
    if os.path.isfile(os.path.join(PACKS, d, 'pack.json')) and d not in order: order.append(d)

out = {'packs': []}
claimed = set()
total = have = 0
for pid in order:
    pdir = os.path.join(PACKS, pid)
    pj = json.load(open(os.path.join(pdir, 'pack.json'), encoding='utf8'))
    sdir = SONGS; os.makedirs(os.path.join(pdir, 'jackets'), exist_ok=True)
    songs = []
    for s in pj['songs']:
        s = dict(s)
        s['available'] = bool(s.get('file')) and s['file'] in PRESENT
        s['size'] = os.path.getsize(os.path.join(sdir, s['file'])) if s['available'] else 0
        songs.append(s)
        claimed.add(s.get('file'))
    pj['songs'] = songs
    pj['count'] = len(songs); pj['available'] = sum(1 for s in songs if s['available'])
    total += pj['count']; have += pj['available']
    out['packs'].append(pj)
    print(f'{pid}: {pj["available"]}/{pj["count"]} zips present')
extra = sorted(PRESENT - claimed)
if extra:
    odir = os.path.join(PACKS, '_other'); os.makedirs(os.path.join(odir, 'jackets'), exist_ok=True)
    songs = []
    for f in extra:
        m, jk = read_manifest(os.path.join(SONGS, f))
        if not m: continue
        lv = max([x.get('level_number', 0) for x in m.get('levels', [])] or [0])
        jname = 'jackets/' + os.path.splitext(f)[0] + '.jpg'
        got = save_jacket(jk, os.path.join(odir, jname)) or os.path.exists(os.path.join(odir, jname))
        art = re.sub(r'\s*\(CV:[^)]*\)', '', m.get('artist_en') or m.get('artist') or '')
        songs.append({'file': f, 'title': m.get('name_en') or m.get('name') or f, 'jp': m.get('name') if m.get('name_en') else '',
                      'artist': art, 'level': lv, 'jacket': jname if got else None, 'available': True,
                      'size': os.path.getsize(os.path.join(SONGS, f))})
    if songs:
        out['packs'].append({'id': '_other', 'title': 'Other songs', 'description': 'Zips found in songs/ that no pack lists yet. Add them to a pack.json to group them.',
                             'banner': None, 'status': 'ready', 'note': '', 'songs': songs, 'count': len(songs), 'available': len(songs)})
        have += len(songs); total += len(songs); print(f'_other: {len(songs)} unlisted zips')
out['generated'] = __import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
json.dump(out, open(os.path.join(ROOT, 'dlc.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(f'dlc.json written: {have}/{total} songs available')
