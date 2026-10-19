"""Run: python run_week3.py. Outputs use the documented default seed."""
from pathlib import Path
import hashlib
import json
import platform
import numpy as np
import pandas as pd
import matplotlib
import seaborn
from simulation import simulate, ASSUMPTIONS
from analysis import analyze


def main():
    root=Path(__file__).resolve().parent
    data=root/'data'; results=root/'results'
    data.mkdir(exist_ok=True);results.mkdir(exist_ok=True)
    print('[1/3] Generating 3,000 simulated shipments (seed 2026)...',flush=True)
    df=simulate();csv=data/'simulated_shipments.csv'
    df.to_csv(csv,index=False,date_format='%Y-%m-%d')
    (data/'simulation_assumptions.json').write_text(json.dumps(ASSUMPTIONS,indent=2),encoding='utf-8')
    print('[2/3] Computing EDA and exporting eight charts...',flush=True)
    metrics=analyze(df,results)
    versions={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
              'matplotlib':matplotlib.__version__,'seaborn':seaborn.__version__}
    (results/'environment.json').write_text(json.dumps(versions,indent=2),encoding='utf-8')
    (results/'dataset_sha256.txt').write_text(hashlib.sha256(csv.read_bytes()).hexdigest()+'  simulated_shipments.csv\n',encoding='utf-8')
    print('[3/3] SUCCESS',flush=True)
    print(f"Simulated shipments: {metrics['rows']:,}; on-time: {metrics['on_time_rate_pct']:.2f}%; mean cost: INR {metrics['mean_cost_inr']:,.2f}")
    print(f'Charts and tables: {results}')
    print('These are hypothetical findings, not actual company performance.')


if __name__=='__main__':
    main()
