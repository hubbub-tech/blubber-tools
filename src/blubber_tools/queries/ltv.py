# customer life time value calculation
# only doing revenue for now, not accounting for costs or margins
# formula: average order value per user * average number of orders per year per user * number of years a user stays with us
# (1 order = 1 item rental, because do not have data on check out carts or combining items in check out)
# sources:
# 1) https://www.netsuite.com/portal/resource/articles/ecommerce/customer-lifetime-value-clv.shtml
# 2) https://corporatefinanceinstitute.com/resources/knowledge/valuation/lifetime-value-calculation/

import pandas as pd
import numpy as np
from metrics import write_reservations_to_pandas, write_orders_to_pandas, write_users_to_pandas
from datetime import date, timedelta

res=write_reservations_to_pandas()
res_cal=res[res.is_calendared==1]
orders=write_orders_to_pandas()
users=write_users_to_pandas()
users['days_since_joined']=date.today()-users['dt_joined'].dt.date

# find users who've been on hubbub for a year or more
# print(users.dtypes)
users=users[users.days_since_joined >= timedelta(365)]
### new
res_cal['date_started']=pd.to_datetime(res_cal['date_started'])
res_cal['date_started']=res_cal['date_started'].dt.date
orders=orders[orders.renter_id.isin(list(users.id))]
orders['res_date_start']=pd.to_datetime(orders['res_date_start'])
orders['res_date_start']=orders['res_date_start'].dt.date

# two ways to do ltv: 1) only using data from users who order, 2) using data from all users, including ones who haven't ordered

# 1) only using data from ordering users (higher ltv)
# avg order value per user, using data from a year ago to today for most updated value:
res_cal=res_cal[(res_cal.renter_id.isin(list(users.id)))&(res_cal.date_started>=date.today()-timedelta(365))]
avg_order_val_1=np.mean(res_cal.groupby('renter_id')['charge'].sum()/res_cal.groupby('renter_id').size())
# avg num orders per user per year, using data from a year ago to today for most updated value:
orders_1yr=orders[orders.res_date_start>=date.today()-timedelta(365)]
avg_num_orders_1=np.mean(orders_1yr.groupby('renter_id').size())
# num years a user stays with us - tbd:
# can do 4 years (length of undergrad)
# or 3 years (length of undergrad - 1 year for discovering hubbub)
# or 3.5 years (length of undergrad - 0.5 year for discovering hubbub)
# what about master, phd students?
# can we use data to estimate?
def ltv_ordering_users(len_retention): # input: number of years a user stays with us
    return avg_order_val_1 * avg_num_orders_1 * len_retention

print("ltv for ordering users, assuming a user stays with us for 3 years: ",ltv_ordering_users(3))
print("ltv for ordering users, assuming a user stays with us for 3.5 years: ",ltv_ordering_users(3.5))
print("ltv for ordering users, assuming a user stays with us for 4 years: ",ltv_ordering_users(4))

# 2) using data from all users (conservative ltv):
# avg order value per user:
non_ordering_users=users[~(users.id.isin(list(orders_1yr.renter_id)))]
res_cal_non_ordering=pd.DataFrame()
for i in non_ordering_users.id:
  res_cal_non_ordering=pd.concat([res_cal_non_ordering,pd.DataFrame([np.nan,np.nan,np.nan,i,0,np.nan]).T])
res_cal_non_ordering.columns=(list(res_cal.columns))
res_cal_all=pd.concat([res_cal,res_cal_non_ordering])
avg_order_val_2=np.mean(res_cal_all.groupby('renter_id')['charge'].sum()/res_cal_all.groupby('renter_id').size())
# avg num orders per user per year:
orders_1yr_non_ordering=pd.DataFrame()
for i in non_ordering_users.id:
  orders_1yr_non_ordering=pd.concat([orders_1yr_non_ordering,pd.DataFrame([np.nan,i,np.nan,np.nan]).T])
orders_1yr_non_ordering.columns=(list(orders_1yr.columns))
orders_1yr_all=pd.concat([orders_1yr,orders_1yr_non_ordering])
avg_num_orders_2=np.mean(orders_1yr_all.groupby('renter_id').count().iloc[:,0])
# ltv:
def ltv_all_users(len_retention): # input: number of years a user stays with us
    return avg_order_val_2 * avg_num_orders_2 * len_retention

print("ltv for all users, assuming a user stays with us for 3 years: ",ltv_all_users(3))
print("ltv for all users, assuming a user stays with us for 3.5 years: ",ltv_all_users(3.5))
print("ltv for all users, assuming a user stays with us for 4 years: ",ltv_all_users(4))
