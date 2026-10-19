import unittest
import pandas as pd
import numpy as np
from simulation import simulate, validate
from analysis import grouped, NUMERIC


class Week3Tests(unittest.TestCase):
    def setUp(self):
        self.df=simulate(100)

    def test_reproducibility(self):
        pd.testing.assert_frame_equal(self.df,simulate(100))

    def test_different_seed(self):
        self.assertFalse(self.df.equals(simulate(100,2027)))

    def test_invalid_size(self):
        for n in [0,-1,2.5]:
            with self.assertRaises(ValueError):simulate(n)

    def test_full_size_and_schema(self):
        df=simulate();self.assertEqual(df.shape,(3000,19));validate(df)

    def test_duplicate_rejected(self):
        df=self.df.copy();df.loc[1,'shipment_id']=df.loc[0,'shipment_id']
        with self.assertRaises(ValueError):validate(df)

    def test_missing_rejected(self):
        df=self.df.copy();df.loc[0,'distance_km']=np.nan
        with self.assertRaises(ValueError):validate(df)

    def test_negative_rejected(self):
        df=self.df.copy();df.loc[0,'warehouse_dwell_hours']=-1
        with self.assertRaises(ValueError):validate(df)

    def test_dates_rejected(self):
        df=self.df.copy();df.loc[0,'delivery_date']+=pd.Timedelta(days=1)
        with self.assertRaises(ValueError):validate(df)

    def test_flag_rejected(self):
        df=self.df.copy();df.loc[0,'late_flag']=1-df.loc[0,'late_flag']
        with self.assertRaises(ValueError):validate(df)

    def test_cost_rejected(self):
        df=self.df.copy();df.loc[0,'transport_cost_inr']+=10
        with self.assertRaises(ValueError):validate(df)

    def test_unknown_category(self):
        df=self.df.copy();df.loc[0,'region']='Unknown'
        with self.assertRaises(ValueError):validate(df)

    def test_fractional_days(self):
        df=self.df.copy();df['promised_days']=df.promised_days.astype(float)
        df.loc[0,'promised_days']=1.5
        with self.assertRaises(ValueError):validate(df)

    def test_hand_calculated_aggregation(self):
        df=self.df.iloc[:2].copy();df['region']='North'
        df['shipment_units']=[10,30];df['transport_cost_inr']=[100.,300.]
        df['late_flag']=[0,1];df['delivery_days']=[2,4]
        row=grouped(df,'region').loc['North']
        self.assertEqual(row.shipments,2);self.assertEqual(row.units,40)
        self.assertEqual(row.on_time_rate_pct,50);self.assertEqual(row.cost_per_unit_inr,10)
        self.assertEqual(row.mean_delivery_days,3)

    def test_group_totals_reconcile(self):
        for key in ['region','service']:
            g=grouped(self.df,key)
            self.assertEqual(g.shipments.sum(),len(self.df))
            self.assertEqual(g.units.sum(),self.df.shipment_units.sum())
            self.assertAlmostEqual(g.total_cost_inr.sum(),self.df.transport_cost_inr.sum())

    def test_correlations_symmetric(self):
        for method in ['pearson','spearman']:
            c=self.df[NUMERIC].corr(method=method)
            self.assertTrue(np.allclose(c,c.T));self.assertTrue(np.allclose(np.diag(c),1))


if __name__=='__main__':unittest.main()
