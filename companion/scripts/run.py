"""Execute chapter notebooks with the current environment's Python kernel."""
from pathlib import Path
import argparse
import json
import sys
import time
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from author import build
from provenance import inputs,digest

ROOT=Path(__file__).resolve().parents[1]

def execute(chapters, profile='complete'):
    reports=[]
    for source in sorted((ROOT/'lessons').glob('*.py')):
        number=int(source.name[:2])
        if chapters and number not in chapters: continue
        if profile=='core' and number in [13,14,15,16]:
            skipped=dict(chapter=number,status='skipped',reason='core profile')
            (ROOT/'results').mkdir(exist_ok=True)
            (ROOT/'results'/f'ch{number:02d}-execution.json').write_text(json.dumps(skipped,indent=2)+'\n')
            reports.append(skipped)
            continue
        provenance=inputs(source)                      # hash the inputs before anything is written
        nb=build(source,write=False); path=ROOT/'notebooks'/f'{source.stem}.ipynb'
        km=KernelManager(kernel_name='python3')
        km.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
        start=time.monotonic()
        try:
            NotebookClient(nb,km=km,timeout=600,resources={'metadata':{'path':str(ROOT.parent)}}).execute()
            path.parent.mkdir(exist_ok=True); nbformat.write(nb,path)     # the shipped notebook changes only after a run
            result=dict(chapter=number,status='passed',seconds=round(time.monotonic()-start,2))
        except Exception as exc:
            failed=ROOT/'results'/f'{source.stem}-failed.ipynb'; failed.parent.mkdir(exist_ok=True); nbformat.write(nb,failed)
            result=dict(chapter=number,status='failed',error=str(exc),failed_notebook=str(failed.relative_to(ROOT)),seconds=round(time.monotonic()-start,2))
        finally:
            if km.has_kernel: km.shutdown_kernel(now=True)
        result['inputs']=provenance
        if result['status']=='passed':
            result['notebook_sha256']=digest(path)
            journal=ROOT/'results'/f'ch{number:02d}-figures.json'
            result['artifacts']={p:digest(ROOT/p) for f in json.loads(journal.read_text()) for p in f['outputs'].values()}
            result['artifacts'].update({str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'results').glob(f'ch{number:02d}-*') if p.is_file() and p.name!=f'ch{number:02d}-execution.json'})
        reports.append(result)
        (ROOT/'results').mkdir(exist_ok=True)
        (ROOT/'results'/f'ch{number:02d}-execution.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','artifacts','notebook_sha256']}),flush=True)
    return reports

USAGE='''Companion command line.

  run.py chapters --all | --chapter N [--profile core|complete]   execute lesson notebooks
  run.py apply --chapter N --input x.csv --config c.json --output DIR   apply one chapter to your data
  run.py forecast --input panel.csv --output DIR [--engine full] ...    forecast many series (see forecast --help)

Applied outputs go in a new, empty directory outside companion/ or under companion/applied-runs/.
'''

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=USAGE,formatter_class=argparse.RawDescriptionHelpFormatter)
    sub=parser.add_subparsers(dest='command',required=True,metavar='{chapters,apply,forecast}')
    ch=sub.add_parser('chapters',help='execute chapter notebooks from their lesson sources')
    ch.add_argument('--all',action='store_true'); ch.add_argument('--chapter',type=int,action='append'); ch.add_argument('--profile',choices=['core','complete'],default='complete')
    ap=sub.add_parser('apply',help='apply a chapter tool to supplied data without changing book artifacts')
    ap.add_argument('--chapter',type=int,required=True); ap.add_argument('--input',required=True); ap.add_argument('--config',required=True); ap.add_argument('--output',required=True)
    fc=sub.add_parser('forecast',help='forecast a panel of series with the batch runner (run.py forecast --help for its options)',add_help=False)
    args,rest=parser.parse_known_args()
    if args.command!='forecast' and rest: parser.error('unrecognized arguments: '+' '.join(rest))
    if args.command=='apply':
        sys.path.insert(0,str(ROOT/'src'))
        from forecasting_companion.applied import run
        try:
            summary=run(args.chapter,args.input,args.config,args.output)
            print(json.dumps(summary,default=str,indent=2))
        except (ValueError,KeyError,FileNotFoundError) as exc:
            parser.exit(2,f'Application stopped: {exc}\n')
        raise SystemExit(0)
    if args.command=='forecast':
        import subprocess
        import os
        env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','')
        raise SystemExit(subprocess.call([sys.executable,'-m','forecasting_companion.batch',*rest],env=env))
    if not args.all and not args.chapter: parser.error('Choose --all or --chapter N')
    reports=execute(set(args.chapter or []),args.profile)
    if not reports or any(r['status']=='failed' for r in reports): sys.exit(1)
