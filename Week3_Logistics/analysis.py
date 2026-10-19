"""Descriptive EDA of simulated shipments; no causal or real-company inference."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from simulation import validate

NUMERIC = ['distance_km','shipment_units','weight_kg','warehouse_dwell_hours','promised_days','delivery_days','transport_cost_inr']
COLORS = ['#285A86','#D98232','#338572','#A64C63']


def grouped(df, key):
    table = df.groupby(key, observed=True).agg(
        shipments=('shipment_id','size'), units=('shipment_units','sum'),
        late_shipments=('late_flag','sum'), mean_delivery_days=('delivery_days','mean'),
        median_delivery_days=('delivery_days','median'),mean_dwell_hours=('warehouse_dwell_hours','mean'),
        mean_distance_km=('distance_km','mean'), total_cost_inr=('transport_cost_inr','sum'),
        mean_cost_inr=('transport_cost_inr','mean'))
    table['late_rate_pct'] = table.late_shipments/table.shipments*100
    table['on_time_rate_pct'] = 100-table.late_rate_pct
    table['cost_per_unit_inr'] = table.total_cost_inr/table.units
    return table


def analyze(df, output):
    validate(df)
    output=Path(output); figures=output/'figures'; figures.mkdir(parents=True,exist_ok=True)
    desc=df[NUMERIC].describe().T
    desc['mode_first']=df[NUMERIC].mode().iloc[0]
    desc['skewness']=df[NUMERIC].skew()
    desc.to_csv(output/'descriptive_statistics.csv',float_format='%.6f')
    work=df.assign(month=df.dispatch_date.dt.strftime('%Y-%m'))
    monthly=grouped(work,'month'); service=grouped(df,'service'); region=grouped(df,'region')
    for name,table in [('monthly',monthly),('service',service),('region',region)]:
        table.to_csv(output/f'{name}_summary.csv',float_format='%.6f')
    pearson=df[NUMERIC].corr(method='pearson'); spearman=df[NUMERIC].corr(method='spearman')
    pearson.to_csv(output/'pearson_correlations.csv'); spearman.to_csv(output/'spearman_correlations.csv')
    comps=['cost_fixed_inr','cost_distance_inr','cost_weight_inr','cost_handling_inr','cost_variation_inr']
    components=df.groupby('service')[comps].mean(); components.to_csv(output/'cost_components_by_service.csv')
    outliers={}
    for col in NUMERIC:
        q1,q3=df[col].quantile([.25,.75]); iqr=q3-q1
        outliers[col]={'iqr':float(iqr),'flagged_rows':int(((df[col]<q1-1.5*iqr)|(df[col]>q3+1.5*iqr)).sum())}
    metrics={
        'source':'Simulated shipments, seed 2026; not actual operational observations',
        'rows':len(df),'columns':len(df.columns),'missing_cells':int(df.isna().sum().sum()),
        'duplicate_ids':int(df.shipment_id.duplicated().sum()),
        'dispatch_start':str(df.dispatch_date.min().date()), 'dispatch_end':str(df.dispatch_date.max().date()),
        'delivery_end':str(df.delivery_date.max().date()),
        'units':int(df.shipment_units.sum()), 'late_shipments':int(df.late_flag.sum()),
        'on_time_rate_pct':float((1-df.late_flag.mean())*100),
        'total_cost_inr':float(df.transport_cost_inr.sum()),
        'mean_cost_inr':float(df.transport_cost_inr.mean()),
        'cost_per_unit_inr':float(df.transport_cost_inr.sum()/df.shipment_units.sum()),
        'mean_delivery_days':float(df.delivery_days.mean()),'median_delivery_days':float(df.delivery_days.median()),
        'p90_delivery_days':float(df.delivery_days.quantile(.9)),
        'mean_dwell_hours':float(df.warehouse_dwell_hours.mean()),
        'distance_cost_pearson':float(pearson.loc['distance_km','transport_cost_inr']),
        'distance_cost_spearman':float(spearman.loc['distance_km','transport_cost_inr']),
        'dwell_delivery_pearson':float(pearson.loc['warehouse_dwell_hours','delivery_days']),
        'component_share_pct':(df[comps].sum()/df.transport_cost_inr.sum()*100).to_dict(),
        'outliers_retained':outliers,
        'monthly':monthly.reset_index().to_dict('records'),
        'service':service.reset_index().to_dict('records'),
        'region':region.reset_index().to_dict('records')}
    (output/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    sns.set_theme(style='whitegrid',font_scale=1.05,palette=COLORS)
    def save(fig,name):
        fig.suptitle('SIMULATED LOGISTICS — JAN–JUN 2026',fontsize=10,color='#555555',y=.995)
        fig.text(.5,.015,'Source: reproducible fictional simulation, seed 2026; not measured company performance.',ha='center',fontsize=9,color='#555555')
        fig.tight_layout(rect=[0,.055,1,.965]);fig.savefig(figures/name,dpi=180);plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(9,6),sharex=True)
    for ax,col,label in [(axes[0],'shipments','Shipments (count)'),(axes[1],'units','Shipment volume (units)')]:
        ax.plot(monthly.index,monthly[col],marker='o',color=COLORS[0]);ax.set_ylabel(label)
    axes[0].set_title('Dispatch volume by month');axes[1].set_xlabel('Dispatch month')
    save(fig,'01_monthly_volume.png')
    fig,ax=plt.subplots(figsize=(9,5));bins=np.arange(.5,df.delivery_days.max()+1.5,1)
    ax.hist(df.delivery_days,bins=bins,color=COLORS[0],edgecolor='white')
    ax.axvline(df.delivery_days.mean(),color=COLORS[1],ls='--',label=f'Mean {df.delivery_days.mean():.2f} days')
    ax.axvline(df.delivery_days.median(),color=COLORS[2],ls=':',label=f'Median {df.delivery_days.median():.0f} days')
    ax.set(title='Actual delivery-day distribution',xlabel='Actual delivery time (days)',ylabel='Shipments (count)');ax.legend()
    save(fig,'02_delivery_distribution.png')
    fig,ax=plt.subplots(figsize=(9,5));sns.boxplot(data=df,x='service',y='delivery_days',order=['Standard','Express'],color=COLORS[0],ax=ax)
    ax.set(title='Delivery-time spread by service',xlabel='Service',ylabel='Actual delivery time (days)')
    save(fig,'03_service_boxplot.png')
    fig,axes=plt.subplots(1,2,figsize=(9,5))
    s=service.reindex(['Standard','Express']); labels=[f'{name}\n(n={int(row.shipments)})' for name,row in s.iterrows()]
    for ax,col,title,ylabel in [(axes[0],'on_time_rate_pct','Within promised time','On-time shipments (%)'),(axes[1],'mean_cost_inr','Mean transportation cost','INR / shipment')]:
        bars=ax.bar(labels,s[col],color=COLORS[:2]);ax.set(title=title,ylabel=ylabel);ax.bar_label(bars,fmt='%.1f',padding=3);ax.set_ylim(0,s[col].max()*1.2)
    save(fig,'04_service_sla_cost.png')
    fig,ax=plt.subplots(figsize=(9,5));sns.scatterplot(data=df,x='distance_km',y='transport_cost_inr',hue='service',hue_order=['Standard','Express'],palette=COLORS[:2],alpha=.35,s=12,ax=ax)
    ax.set(title='Distance and transport cost: all 3,000 shipments',xlabel='Route distance (km)',ylabel='Transportation cost (INR)')
    save(fig,'05_distance_cost.png')
    fig,ax=plt.subplots(figsize=(10,7));names=['Distance','Units','Weight','Dwell','Promise','Delivery','Cost']
    sns.heatmap(pearson,annot=True,fmt='.2f',cmap='vlag',vmin=-1,vmax=1,center=0,xticklabels=names,yticklabels=names,ax=ax,square=True,cbar_kws={'label':'Pearson r'})
    ax.set_title('Pearson correlations: original measurement units')
    save(fig,'06_correlation_heatmap.png')
    fig,axes=plt.subplots(1,2,figsize=(9,5));r=region.sort_values('mean_dwell_hours')
    for ax,col,title,ylabel in [(axes[0],'mean_dwell_hours','Warehouse dwell by region','Mean dwell (hours)'),(axes[1],'late_rate_pct','Missed promises by region','Late shipments (%)')]:
        labels=[f'{name}\n(n={int(row.shipments)})' for name,row in r.iterrows()]
        bars=ax.bar(labels,r[col],color=COLORS);ax.set(title=title,ylabel=ylabel);ax.bar_label(bars,fmt='%.1f',padding=3);ax.set_ylim(0,r[col].max()*1.2)
    save(fig,'07_region_bottleneck.png')
    fig,ax=plt.subplots(figsize=(9,5));c=components.reindex(['Standard','Express']);bottom=np.zeros(2)
    component_colors=[COLORS[0],COLORS[1],COLORS[2],COLORS[3],'#848B96']
    for col,label,color in zip(comps,['Fixed','Distance','Weight','Handling','Variation'],component_colors):
        ax.bar(c.index,c[col],bottom=bottom,label=label,color=color);bottom+=c[col].to_numpy()
    ax.set(title='Programmed mean cost components by service',ylabel='Mean cost (INR / shipment)',xlabel='Service');ax.legend(loc='upper left',bbox_to_anchor=(1,1))
    save(fig,'08_cost_components.png')
    return metrics
