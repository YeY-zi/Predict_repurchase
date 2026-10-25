"""Check local publication links, source hashes and recorded result arithmetic."""
from pathlib import Path
import ast,json,hashlib,re,zipfile
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
errors=[]
for p in ROOT.rglob('*.md'):
    if any(x in p.parts for x in ['.git','.venv','outputs','data/raw']):continue
    text=p.read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if re.match(r'^[a-zA-Z]+:',target) or target.startswith('#'):continue
        target=unquote(target.split('#')[0].strip('<>'))
        if target and not (p.parent/target).exists():errors.append(f'Missing link: {p.relative_to(ROOT)} -> {target}')
for p in (ROOT/'scripts').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
m=json.loads((ROOT/'data/source-manifest.json').read_text(encoding='utf-8'))
archive=ROOT/'data/olist-v2.zip'
if archive.exists():
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==m['zip_sha256']
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for item in m['files']:assert hashlib.sha256(z.read(item['name'])).hexdigest()==item['sha256']
report=json.loads((ROOT/'results/classification/model-comparison.json').read_text(encoding='utf-8'))
for record in report['models'].values():
    r=record['test'];assert abs(r['Precision_at_10pct']-r['hits']/r['selected'])<1e-12
    assert abs(r['Recall_at_10pct']-r['hits']/299)<1e-12
audit=json.loads((ROOT/'results/cleaning-audit.json').read_text(encoding='utf-8'))
assert audit['orders_raw']==audit['approved_positive_value_orders_used']+audit['orders_not_used_for_approval_based_analysis']
assert audit['raw_files_modified'] is False
feedback=json.loads((ROOT/'results/feedback/results.json').read_text(encoding='utf-8'))
assert feedback['selected']==max(feedback['validation'],key=lambda name:feedback['validation'][name]['AP'])
for phase,total in [('train',21160),('validation',29368),('test',37813)]:
    assert sum(row['customers'] for row in feedback['profiles'][phase])==total
assert sum(row['baseline_top10_hits'] for row in feedback['profiles']['validation'])==feedback['validation']['baseline']['hits']
assert sum(row['baseline_top10_selected'] for row in feedback['profiles']['validation'])==feedback['validation']['baseline']['selected']
for path in (ROOT/'notebooks').glob('*.ipynb'):
    nb=json.loads(path.read_text(encoding='utf-8'))
    assert not [o for c in nb['cells'] if c['cell_type']=='code' for o in c.get('outputs',[]) if o.get('output_type')=='error']
with zipfile.ZipFile(ROOT/'slides/olist-repurchase-briefing.pptx') as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)])==5
if errors:raise ValueError('\n'.join(errors))
print('PASS: Markdown links, Python syntax, optional downloaded archive hashes, cleaning and feedback arithmetic, notebook saved outputs, 5-slide proposal PPTX.')
