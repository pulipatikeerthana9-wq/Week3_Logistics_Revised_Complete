import unittest
import pandas as pd
from feedback_analysis import calculate


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.df=pd.DataFrame({'shipment_id':[1,2,3,4], 'service':['Express','Express','Standard','Standard'],
            'region':['East','South','East','South'],'dispatch_date':['2026-01-01']*4,
            'distance_km':[300.,600.,900.,901.], 'transport_cost_inr':[100.,200.,300.,400.],
            'warehouse_dwell_hours':[20.,8.,20.,8.], 'delivery_days':[2,1,4,3],
            'promised_days':[1,1,3,3], 'delay_days':[1,0,1,0], 'late_flag':[1,0,1,0],
            'weight_kg':[10.,20.,30.,40.], 'shipment_units':[5,10,15,20]})
    def test_bins_cover_each_record_once(self):
        t=calculate(self.df)[1]
        self.assertEqual(t.shipments.sum(),4)
        self.assertEqual(t.distance_band.astype(str).tolist(),['0–300','>300–600','>600–900','>900'])
    def test_region_rates(self):
        t=calculate(self.df)[2]
        self.assertTrue((t.loc[t.location=='East','late_pct']==100).all())
        self.assertTrue((t.loc[t.location=='Non-East','late_pct']==0).all())
    def test_frequency_reconciles(self):
        t=calculate(self.df)[3]
        self.assertEqual(t.shipments.sum(),4); self.assertAlmostEqual(t.share_pct.sum(),100)
    def test_calendar_denominator(self):
        t=calculate(self.df)[4]
        self.assertAlmostEqual(t.shipments_per_calendar_day.iloc[0],4/31)


if __name__=='__main__': unittest.main()
