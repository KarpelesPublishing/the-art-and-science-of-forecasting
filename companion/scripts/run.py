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
  run.py brief --output brief.json [--target ... --horizon N ...]     write the forecasting brief; prints the questions still open
  run.py profile --input x.csv [--brief brief.json] [--output DIR]     look at the data before modelling: frequency, season, gaps, route
  run.py apply --chapter N --input x.csv --config c.json --output DIR [--brief brief.json]   apply one chapter to your data
  run.py report --run DIR                                              render report.md and claims.json from the run's own artifacts
  run.py journal add --run DIR | score --actuals a.csv | calibration     keep score: record forecasts, score them when actuals arrive, read your track record
  run.py forecast --input panel.csv --output DIR [--engine full] ...    forecast many series (see forecast --help)

Applied outputs go in a new, empty directory outside companion/ or under companion/applied-runs/.
'''

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=USAGE,formatter_class=argparse.RawDescriptionHelpFormatter)
    sub=parser.add_subparsers(dest='command',required=True,metavar='{brief,profile,apply,report,journal,forecast,chapters}')
    ch=sub.add_parser('chapters',help='execute chapter notebooks from their lesson sources')
    ch.add_argument('--all',action='store_true'); ch.add_argument('--chapter',type=int,action='append'); ch.add_argument('--profile',choices=['core','complete'],default='complete')
    ap=sub.add_parser('apply',help='apply a chapter tool to supplied data without changing book artifacts')
    ap.add_argument('--chapter',type=int,required=True); ap.add_argument('--input',required=True); ap.add_argument('--config',required=True); ap.add_argument('--output',required=True); ap.add_argument('--brief',help='brief.json from `run.py brief`; its horizon, frequency, cutoff and units override the config')
    pr=sub.add_parser('profile',help='describe a timestamp,target series and recommend a route before any model runs')
    pr.add_argument('--input',required=True); pr.add_argument('--config'); pr.add_argument('--brief',help='brief.json: its horizon, frequency and cutoff shape the profile'); pr.add_argument('--output',help='directory for profile.json (default: print only)'); pr.add_argument('--json',action='store_true',help='print the full profile as JSON')
    br=sub.add_parser('brief',help='write or check a forecasting brief; unanswered questions are printed for the interview')
    br.add_argument('--output',required=True,help='path of brief.json to write (an existing file is loaded and updated)')
    for key in ('target','units','decision','frequency','as_of','cost_of_over','cost_of_under','known_in_advance','outcome_date','audience','source'):br.add_argument('--'+key.replace('_','-'),dest=key)
    br.add_argument('--horizon',type=int)
    rp=sub.add_parser('report',help='render report.md and claims.json from a finished run directory')
    rp.add_argument('--run',required=True); rp.add_argument('--check',help='a text file of your interpretation; numbers not supported by claims.json are listed'); rp.add_argument('--also',action='append',default=[],help='another run directory whose claims also count for --check (repeatable)')
    jn=sub.add_parser('journal',help='record, score and review forecasts')
    jn.add_argument('action',choices=['add','score','calibration','list']); jn.add_argument('--run'); jn.add_argument('--actuals'); jn.add_argument('--id'); jn.add_argument('--note',default=''); jn.add_argument('--column',help='journal this results.csv column instead of forecast (for example break_scenario)')
    jn.add_argument('--journal',default=str(ROOT/'applied-runs/journal/forecasts.jsonl'))
    fc=sub.add_parser('forecast',help='forecast a panel of series with the batch runner (run.py forecast --help for its options)',add_help=False)
    args,rest=parser.parse_known_args()
    if args.command!='forecast' and rest: parser.error('unrecognized arguments: '+' '.join(rest))
    if args.command=='apply':
        sys.path.insert(0,str(ROOT/'src'))
        from forecasting_companion.applied import run
        try:
            summary=run(args.chapter,args.input,args.config,args.output,brief_path=args.brief)
            print(json.dumps(summary,default=str,indent=2))
        except (ValueError,KeyError,FileNotFoundError) as exc:
            parser.exit(2,f'Application stopped: {exc}\n')
        raise SystemExit(0)
    if args.command=='report':
        sys.path.insert(0,str(ROOT/'src'))
        from pathlib import Path as _P
        from forecasting_companion.report import render,check_claims
        try:
            text,claims=render(args.run)
        except (FileNotFoundError,ValueError) as exc:
            parser.exit(2,f'Report stopped: {exc}\n')
        print(f'wrote {_P(args.run)/"report.md"} and claims.json ({len(claims)} sourced numbers)')
        if args.check:
            from forecasting_companion.report import load_claims
            if args.also:claims=claims+load_claims(*args.also)
            bad=check_claims(_P(args.check).read_text(),claims)
            print('every number in the interpretation is supported by the run' if not bad else 'numbers with no source in this run: '+', '.join(bad))
            raise SystemExit(0 if not bad else 4)
        raise SystemExit(0)
    if args.command=='journal':
        sys.path.insert(0,str(ROOT/'src'))
        from forecasting_companion import journal as J
        try:
            if args.action=='add':
                if not args.run:parser.error('journal add needs --run DIR')
                e=J.add(args.run,args.journal,args.note,args.column); print(f'journaled {e["id"]}: {e["target"]} ({len(e["forecasts"])} periods, outcome due {e["outcome_due"]})')
            elif args.action=='score':
                if not args.actuals:parser.error('journal score needs --actuals file.csv with timestamp,actual')
                scored=J.score(args.actuals,args.journal,args.id)
                for e in scored:print(f'{e["id"]} {e["target"]}: MAE {e["scores"]["mae"]:.4g}, bias {e["scores"]["bias"]:+.4g}'+(f', band coverage {e["scores"]["band_coverage"]:.0%}' if e["scores"].get("band_coverage") is not None else '')+f' over {e["scores"]["scored_periods"]} periods')
                if not scored:print('no journal entry matched those timestamps')
            elif args.action=='calibration':
                out,text=J.calibration(args.journal); print(text)
            else:
                for e in J.load(args.journal):print(f'{e["id"]}  {e["created_at"][:10]}  ch{e["chapter"]}  {e["target"]}  {"scored" if e.get("scores") else "pending, due "+str(e["outcome_due"])}')
        except (ValueError,FileNotFoundError) as exc:
            parser.exit(2,f'Journal stopped: {exc}\n')
        raise SystemExit(0)
    if args.command=='profile':
        sys.path.insert(0,str(ROOT/'src'))
        import pandas as pd
        from pathlib import Path as _P
        from forecasting_companion.profile import profile_series,describe
        from forecasting_companion.applied.core import clean_json
        config=json.loads(_P(args.config).read_text()) if args.config else {}
        if args.brief:
            from forecasting_companion.brief import Brief
            config={**config,**Brief.load(args.brief).config_overrides()}
        try:
            profile=clean_json(profile_series(pd.read_csv(args.input),config))
        except (ValueError,KeyError) as exc:
            parser.exit(2,f'Profile stopped: {exc}\n')
        print(json.dumps(profile,indent=2) if args.json else describe(profile))
        if args.output:
            out=_P(args.output); out.mkdir(parents=True,exist_ok=True); (out/'profile.json').write_text(json.dumps(profile,indent=2)+'\n'); print(f'\nwrote {out/"profile.json"}')
        raise SystemExit(0)
    if args.command=='brief':
        sys.path.insert(0,str(ROOT/'src'))
        from pathlib import Path as _P
        from forecasting_companion.brief import Brief
        brief=Brief.load(args.output) if _P(args.output).exists() else Brief()
        for key in ('target','units','decision','horizon','frequency','as_of','cost_of_over','cost_of_under','known_in_advance','outcome_date','audience','source'):
            value=getattr(args,key)
            if value not in (None,''):setattr(brief,key,value)
        brief.save(args.output)
        pending=brief.interview(); problems=brief.validate()
        print(brief.describe())
        if pending:print('\nStill to ask:');[print(f'  {i+1}. {q}') for i,(k,q) in enumerate(pending)]
        print('\nUsable for a forecast: '+('yes' if not problems else 'not yet ('+'; '.join(problems)+')'))
        raise SystemExit(0 if not problems else 3)
    if args.command=='forecast':
        import subprocess
        import os
        env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','')
        raise SystemExit(subprocess.call([sys.executable,'-m','forecasting_companion.batch',*rest],env=env))
    if not args.all and not args.chapter: parser.error('Choose --all or --chapter N')
    reports=execute(set(args.chapter or []),args.profile)
    if not reports or any(r['status']=='failed' for r in reports): sys.exit(1)
