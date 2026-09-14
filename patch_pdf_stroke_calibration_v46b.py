from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V46B_PDF_STROKE_CALIBRATION'
if marker in s:
    print('v46b already applied')
    raise SystemExit(0)

anchor='function drawSvgLine(ctx,n)'
if anchor not in s:
    raise SystemExit('v46b: drawSvgLine anchor not found')
s=s.replace(anchor,"let kbPdfStrokeFactorV46=1;\n"+anchor,1)

needle="ctx.lineWidth=+(n.getAttribute('stroke-width')||.2);"
if s.count(needle)<3:
    raise SystemExit('v46b: generic stroke assignments not found')
s=s.replace(needle,"ctx.lineWidth=+(n.getAttribute('stroke-width')||.2)*kbPdfStrokeFactorV46;",3)

old="else if(n.matches?.('g[data-type=\"dimension\"],g[data-type=\"leader\"],g[data-type=\"line\"]'))drawDimensionObject(ctx,n);"
new="else if(n.matches?.('g[data-type=\"dimension\"],g[data-type=\"leader\"],g[data-type=\"line\"]')){const prevStrokeV46=kbPdfStrokeFactorV46;kbPdfStrokeFactorV46=25.4/96;drawDimensionObject(ctx,n);kbPdfStrokeFactorV46=prevStrokeV46;}"
if old not in s:
    raise SystemExit('v46b: PDF annotation branch not found')
s=s.replace(old,new,1)

s=s.replace('let kbPdfStrokeFactorV46=1;',"let kbPdfStrokeFactorV46=1;/* KB911_V46B_PDF_STROKE_CALIBRATION */",1)
for token in [marker,'kbPdfStrokeFactorV46=25.4/96']:
    if token not in s:
        raise SystemExit('v46b guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v46b: PDF annotation stroke weight calibrated to on-screen preview')
