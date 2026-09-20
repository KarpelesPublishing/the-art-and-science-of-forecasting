"""Render all figure pages and chart contact sheets for human/agent inspection."""
from pathlib import Path
import json
import re
import fitz
from PIL import Image,ImageDraw
from audit_pdf import contacts

ROOT=Path(__file__).resolve().parents[1]

def main():
    pdf=ROOT/'revision/output/the-art-and-science-of-forecasting-revised-6x9.pdf'
    doc=fitz.open(pdf); pages=[]; caption_pages={}; outside=[]
    for i,page in enumerate(doc):
        text=page.get_text()
        labels=re.findall(r'Figure (\d+\.\d+)\.',text)
        if labels:
            pages.append(i)
            for label in labels: caption_pages[label]=i+1
        for block in page.get_text('dict')['blocks']:
            if 'lines' not in block: continue
            for line in block['lines']:
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if x0<50 or x1>382 or y0<24 or y1>625:
                        outside.append({'page':i+1,'text':span['text'][:90],'bbox':list(span['bbox'])})
    contacts(pdf,ROOT/'reports/layout-pages',pages)
    # Also inspect standalone charts at a readable thumbnail size.
    manifest=json.loads((ROOT/'manifest.json').read_text()); figures=[f for c in manifest['chapters'] for f in c['figures']]
    folder=ROOT/'reports/chart-sheets'; folder.mkdir(parents=True,exist_ok=True)
    for start in range(0,len(figures),12):
        sheet=Image.new('RGB',(1500,1550),'white'); draw=ImageDraw.Draw(sheet)
        for slot,f in enumerate(figures[start:start+12]):
            im=Image.open(ROOT/f['outputs']['png']).convert('RGB'); im.thumbnail((490,350))
            x=(slot%3)*500; y=(slot//3)*385
            draw.text((x+8,y+5),f['id'],fill='black'); sheet.paste(im,(x,y+25))
        sheet.save(folder/f'charts-{start//12+1:02d}.jpg')
    report={'pages':len(doc),'figure_pages':pages,'caption_pages':caption_pages,'text_outside_generous_print_bounds':outside}
    (ROOT/'reports/layout-inspection.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pages':len(doc),'figure_pages':len(pages),'captions':len(caption_pages),'outside_bounds':len(outside)}))

if __name__=='__main__':main()
