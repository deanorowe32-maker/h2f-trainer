"""Import demo renders into the app.

Usage: python3 tools/import_renders.py <folder or .zip> [...]
Files must be named <exercise id>-a / -b / -m1 / -m2 with any image extension
(the names in docs/demo-photo-prompts.csv). Each is centre-cropped to 3:2,
saved as ph/<name>.jpg at 720x480, and registered in index.html so the app
shows it instead of the old photo or illustration. Phones get the new image
because the photo's version stamp changes.
"""
import sys, re, os, zipfile, tempfile, time
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = re.compile(r'^([a-z0-9_]+)-(a|b|m1|m2)\.(jpe?g|png|webp)$', re.I)

def files(args):
    for a in args:
        if a.lower().endswith('.zip'):
            d = tempfile.mkdtemp()
            zipfile.ZipFile(a).extractall(d)
            a = d
        for dp, _, fs in os.walk(a):
            for f in fs:
                if not f.startswith('.'):
                    yield os.path.join(dp, f)

def main(args):
    html = open(os.path.join(ROOT, 'index.html')).read()
    import csv
    known = {r['File name'].rsplit('-', 1)[0] for r in csv.DictReader(open(os.path.join(ROOT, 'docs', 'demo-photo-prompts.csv')))}
    def obj(name):
        m = re.search(r'const %s=\{(.*?)\};' % name, html)
        return m
    done, skipped, waiting = {}, [], []
    for path in files(args):
        m = NAME.match(os.path.basename(path))
        if not m or m.group(1) not in known:
            skipped.append(os.path.basename(path)); continue
        ex, w = m.group(1), m.group(2).lower()
        im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
        im = ImageOps.fit(im, (720, 480), Image.LANCZOS, centering=(0.5, 0.5))
        im.save(os.path.join(ROOT, 'ph', f'{ex}-{w}.jpg'), quality=82, optimize=True, progressive=True)
        done.setdefault(ex, set()).add(w)
    stamp = time.strftime('%y%m%d%H%M')
    for ex, ws in done.items():
        both = all(os.path.exists(os.path.join(ROOT, 'ph', f'{ex}-{x}.jpg')) for x in 'ab')
        if ws & {'a', 'b'} and not both:
            waiting.append(ex)
        if both and not re.search(r'(^|,)%s:1' % ex, obj('BPH').group(1)):
            html = html.replace('const BPH={', 'const BPH={%s:1,' % ex, 1)
        mids = sorted(ws & {'m1', 'm2'})
        if mids:
            body = obj('BPM').group(1)
            cur = re.search(r'(?:^|,)%s:\[([^\]]*)\]' % ex, body)
            have = set(re.findall(r"'(m\d)'", cur.group(1))) if cur else set()
            new = "%s:[%s]" % (ex, ','.join("'%s'" % x for x in sorted(have | set(mids))))
            body2 = body.replace(cur.group(0).lstrip(','), new) if cur else (body + ',' + new if body else new)
            html = html.replace('const BPM={%s}' % body, 'const BPM={%s}' % body2, 1)
        body = obj('PHV').group(1)
        body = re.sub(r'(^|,)%s:\d+' % ex, '', body).strip(',')
        body = (body + ',' if body else '') + '%s:%s' % (ex, stamp)
        html = re.sub(r'const PHV=\{.*?\};', 'const PHV={%s};' % body, html, count=1)
    open(os.path.join(ROOT, 'index.html'), 'w').write(html)
    print(f'Imported {sum(len(v) for v in done.values())} images for {len(done)} exercises.')
    if waiting: print('Waiting for the other position before showing:', ', '.join(sorted(waiting)))
    if skipped: print('Skipped (name not recognised):', ', '.join(sorted(skipped)))

if __name__ == '__main__':
    main(sys.argv[1:])
