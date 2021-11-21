import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
from blubber_orm import Users, Reservations, Orders
# from utils import data_to_csv

## make pandas dataframes for reservations, orders, users
res_li=[]
res=Reservations.get_all()
for reservation in res:
    res_li.append([reservation.date_started,reservation.date_ended,reservation.is_calendared,reservation.renter_id,reservation._charge,reservation.dt_created])
res=pd.DataFrame(res_li,columns=['date_started','date_ended','is_calendared','renter_id','charge','dt_created'])
# print(res)
orders_li=[]
orders=Orders.get_all()
for order in orders:
    orders_li.append([order.date_placed,order.renter_id,order.res_date_start,order.res_date_end])
# print(type(orders))
orders=pd.DataFrame(orders_li,columns=['date_placed','renter_id','res_date_start','res_date_end'])
# print(orders)
users_li=[]
users=Users.get_all()
for user in users:
    users_li.append([user.dt_joined])
users=pd.DataFrame(users_li,columns=['dt_joined'])
# print(users)#

## make columns datetime
users['dt_joined']=pd.to_datetime(users['dt_joined']) # add dt_joined for est/edt
users['dt_joined_et']=users.dt_joined.dt.tz_localize('UTC').dt.tz_convert('US/Eastern').dt.strftime("%Y-%m-%d %H:%M:%S")
# users['dt_last_active']=pd.to_datetime(users['dt_last_active']) # not et
# users['renter_id']=users['id']
users['days_since_joined']=date.today()-users['dt_joined'].dt.date # not et
orders['date_placed']=pd.to_datetime(orders['date_placed'])
orders['date_placed']=orders['date_placed'].dt.date
orders['res_date_start']=pd.to_datetime(orders['res_date_start'])
orders['res_date_end']=pd.to_datetime(orders['res_date_end'])
orders['duration']=orders.res_date_end-orders.res_date_start
res['date_started']=pd.to_datetime(res['date_started']) # use date started, date ended, renter id, item id to get things before july 2021
res['date_ended']=pd.to_datetime(res['date_ended'])
res['dt_created']=pd.to_datetime(res['dt_created']) # add dt_created for est/edt
res['dt_created_et']=res.dt_created.dt.tz_localize('UTC').dt.tz_convert('US/Eastern').dt.strftime("%Y-%m-%d %H:%M:%S")
res['date_created']=res['dt_created'].dt.date
res['duration']=res.date_ended-res.date_started

res_cal=res[res.is_calendared==1] ## orders within reservations

current_mo=str(datetime.now().year)+'-'+str(datetime.now().month)
## auto generate month lists
# inputs: what month to start, what month to end, default is all data up to today
# input format: 'yyyy-mm', eg. generate_date_li('2021-01','2021-09')
def generate_date_li(start_mo='2020-09',end_mo=current_mo):
    # print('start month: ',start_mo,'end month :',end_mo)
    if end_mo==current_mo:
        # print('end month = current month')
        if current_mo.split('-')[1] != '12':
            # print('end/current month is not 12')
            mo_ends=list(pd.date_range(start=start_mo, end=str(datetime.now().year)+'-'+str(datetime.now().month+1), freq='M').astype(str))
        else:
            # print('end/current month is 12')
            mo_ends=list(pd.date_range(start=start_mo, end=str(datetime.now().year+1)+'-01', freq='M').astype(str))
    else:
        # print('end month is not current month')
        if end_mo.split('-')[1] != '12':
            # print('end/current month is not 12')
            mo_ends=list(pd.date_range(start=start_mo, end=end_mo.split('-')[0]+'-'+str(int(end_mo.split('-')[1])+1), freq='M').astype(str))
        else:
            # print('end/current month is 12')
            mo_ends=list(pd.date_range(start=start_mo, end=str(int(end_mo.split('-')[0])+1)+'-01', freq='M').astype(str))
    mo_starts=[]
    for i in mo_ends:
        mo_starts.append(i.split('-')[0]+'-'+i.split('-')[1]+'-01')
    datestrs=[list(x) for x in zip(mo_starts, mo_ends)]
    # print(datestrs)
    datetimes=[]
    for i in datestrs:
        datetimes.append([date(int(i[0].split('-')[0]),int(i[0].split('-')[1]),int(i[0].split('-')[2])), date(int(i[1].split('-')[0]),int(i[1].split('-')[1]),int(i[1].split('-')[2]))])
    # print(datetimes)
    months=[]
    for i in mo_ends:
        months.append([i.split('-')[0]+'-'+i.split('-')[1]])
    # print(months)
    dateli=[a + b +c for a, b, c in zip(datestrs, datetimes,months)]
    return dateli

# print(generate_date_li('2020-12','2021-06'))

# dateli = generate_date_li() ## default: all data
# print(dateli)

def avg_amt_spent_per_item(rev,rentals_started):
  try:
    a=rev/rentals_started
  except ZeroDivisionError:
    a=0
  return a

def items_per_ordering_user(orders,ordering_users):
  try:
    a=orders/ordering_users
  except ZeroDivisionError:
    a=0
  return a

def metrics_df(res_cal=res_cal, orders=orders, users=users, start_mo='2020-09' , end_mo=current_mo):
    df=pd.DataFrame()
    dateli=generate_date_li(start_mo,end_mo)
    for i in dateli:
        # print(i)
        rev_mo=res_cal[(res_cal.date_started>=i[0])&(res_cal.date_started<=i[1])].charge.sum()
        cum_rev_mo=res_cal[res_cal.date_started<=i[1]].charge.sum()
        ordering_users_mo=orders[(orders.date_placed>=i[2])&(orders.date_placed<=i[3])].renter_id.nunique()
        users_joined_mo=len(users[(users.dt_joined_et>=i[0])&(users.dt_joined_et<=i[1])])
        cum_users_mo=len(users[users.dt_joined_et<=i[1]])
        orders_mo=len(orders[(orders.date_placed>=i[2])&(orders.date_placed<=i[3])]) # number of items rented
        cum_orders_mo=len(orders[(orders.date_placed<=i[3])])
        rentals_started_mo=len(orders[(orders.res_date_start>=i[0])&(orders.res_date_start<=i[1])])
        cum_rentals_started=len(orders[(orders.res_date_start<=i[1])])
        # avg_amt_spent_per_item_mo=rev_mo/orders_mo # average amount spent on each item
        avg_amt_spent_per_item_mo=avg_amt_spent_per_item(rev_mo,rentals_started_mo)
        # print(rev_mo/orders_mo)
        # print(rev_mo/len(res_cal[(res_cal.date_started>=i[0])&(res_cal.date_started<=i[1])]))
        # items_per_ordering_user_mo=orders_mo/ordering_users_mo
        items_per_ordering_user_mo=items_per_ordering_user(orders_mo,ordering_users_mo)
        pct_users_ordering_mo=ordering_users_mo/cum_users_mo
        # all of above goes into a column for that month
        df=pd.concat([df,pd.DataFrame([rev_mo,cum_rev_mo,ordering_users_mo,users_joined_mo,cum_users_mo,orders_mo,cum_orders_mo,
                 rentals_started_mo,cum_rentals_started,avg_amt_spent_per_item_mo,items_per_ordering_user_mo,pct_users_ordering_mo],columns=[i[4]])],axis=1)

    df.index=['revenue by month','cumulative revenue','ordering users by month','users joined by month',
              'cumulative users','items ordered by month','cumulative items ordered','rentals started by month',
              'cumulative rentals started','average amount user spent on each item by month',
              'items per ordering user by month','percent users ordering by month']

# print(df)
    # df.to_csv('metrics.csv') # generate metrics csv
    return df

df=metrics_df() #res_cal, orders, users)
df.to_csv('metrics.csv') # generate metrics csv
pct_growth_monthly=metrics.pct_change(axis='columns') # percentages are in fraction form, not multiplied by 100
pct_growth_yoy=metrics.pct_change(axis='columns',periods=12).dropna(axis=1,how='all') # percentages are in fraction form, not multiplied by 100
pct_growth_monthly.to_csv('pct_growth_monthly.csv')
pct_growth_yoy.to_csv('pct_growth_yoy.csv')
