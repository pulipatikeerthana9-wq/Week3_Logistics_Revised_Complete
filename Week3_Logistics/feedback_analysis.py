"""Deeper EDA on the unchanged hypothetical dataset; no causal intervention.
Run after run_week3.py: python feedback_analysis.py
"""
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parent
PAIRS = [('distance_km', 'transport_cost_inr'),
         ('warehouse_dwell_hours', 'delivery_days'),
         ('weight_kg', 'transport_cost_inr'),
         ('shipment_units', 'weight_kg'),
         ('distance_km', 'delivery_days')]


def calculate(df):
    corr = []
    for name, part in [('All', df), *list(df.groupby('service'))]:
        for x, y in PAIRS:
            corr.append({'group': name, 'n': len(part), 'x': x, 'y': y,
                         'pearson': part[x].corr(part[y], method='pearson'),
                         'spearman': part[x].corr(part[y], method='spearman')})
    work = df.assign(distance_band=pd.cut(df.distance_km, [0,300,600,900,float('inf')],
                                         labels=['0–300','>300–600','>600–900','>900'], right=True),
                     location=df.region.where(df.region == 'East', 'Non-East'))
    def summarize(keys):
        return work.groupby(keys, observed=True).agg(
            shipments=('shipment_id','size'), late=('late_flag','sum'),
            mean_days=('delivery_days','mean'), mean_dwell=('warehouse_dwell_hours','mean'),
            mean_distance=('distance_km','mean'), mean_cost=('transport_cost_inr','mean')).assign(
                late_pct=lambda t:t.late/t.shipments*100).reset_index()
    bands=summarize(['distance_band','service'])
    regions=summarize(['service','location'])
    freq=df.groupby('delivery_days').size().rename('shipments').reset_index()
    freq['share_pct']=freq.shipments/len(df)*100
    monthly=df.assign(month=pd.to_datetime(df.dispatch_date).dt.to_period('M')).groupby('month').size().rename('shipments').reset_index()
    monthly['calendar_days']=monthly.month.dt.days_in_month
    monthly['shipments_per_calendar_day']=monthly.shipments/monthly.calendar_days
    monthly['month']=monthly.month.astype(str)
    examples = df.loc[(df.service=='Express') & (df.delivery_days>df.promised_days),
                      ['service','distance_km','warehouse_dwell_hours','promised_days','delivery_days','delay_days']].head(1)
    metrics={'scope':'Unchanged hypothetical simulation; stratified associations, not causal effects',
             'express_share_of_late_pct':df.loc[df.service=='Express','late_flag'].sum()/df.late_flag.sum()*100,
             'east_share_of_late_pct':df.loc[df.region=='East','late_flag'].sum()/df.late_flag.sum()*100,
             'delivery_four_plus':int((df.delivery_days>=4).sum()),
             'express_late_example':examples.to_dict('records')}
    return pd.DataFrame(corr), bands, regions, freq, monthly, metrics


def main():
    df=pd.read_csv(BASE/'data/simulated_shipments.csv')
    results=calculate(df)
    out=BASE/'results/feedback';out.mkdir(parents=True,exist_ok=True)
    for name,frame in zip(['correlations_by_service','distance_service','east_by_service','delivery_frequency','daily_volume'],results[:5]):
        frame.to_csv(out/f'{name}.csv',index=False)
        print('\n'+name+'\n'+frame.to_string(index=False))
    (out/'evidence.json').write_text(json.dumps(results[5],indent=2),encoding='utf-8')
    print(json.dumps(results[5],indent=2))


if __name__ == '__main__': main()
