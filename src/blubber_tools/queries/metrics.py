import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

from blubber_orm import get_db
from blubber_orm import Users, Reservations, Orders
# from utils import data_to_csv

## make pandas dataframes for reservations, orders, users
def write_reservations_to_pandas():
    database = get_db() # @notice: database is an object containing psycopg.cursor and pscopg.connection

    SQL = "SELECT date_started, date_ended, is_calendared, renter_id, charge, dt_created FROM reservations"

    database.cursor.execute(SQL)
    results = database.cursor.fetchall() # @notice: result is a list of tuples

    res_pandas = pd.DataFrame(
        results,
        columns=['date_started','date_ended','is_calendared','renter_id','charge','dt_created']
    )
    return res_pandas

def write_orders_to_pandas():
    database = get_db() # @notice: database is an object containing psycopg.cursor and pscopg.connection

    SQL = "SELECT date_placed, renter_id, res_date_start, res_date_end FROM orders"

    database.cursor.execute(SQL)
    results = database.cursor.fetchall() # @notice: result is a list of tuples

    orders_pandas = pd.DataFrame(
        results,
        columns=['date_placed','renter_id','res_date_start','res_date_end']
    )
    return orders_pandas

def write_users_to_pandas():
    database = get_db() # @notice: database is an object containing psycopg.cursor and pscopg.connection

    SQL = "SELECT dt_joined FROM users"

    database.cursor.execute(SQL)
    results = database.cursor.fetchall() # @notice: result is a list of tuples

    users_pandas = pd.DataFrame(results, columns=['dt_joined'])
    return users_pandas

res = write_reservations_to_pandas()
orders = write_orders_to_pandas()
users = write_users_to_pandas()

## make columns datetime
users['dt_joined']=pd.to_datetime(users['']) # add dt_joined for est/edt
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
    if end_mo==current_mo:
        if current_mo.split('-')[1] != '12':
            mo_ends=list(pd.date_range(start=start_mo, end=str(datetime.now().year)+'-'+str(datetime.now().month+1), freq='M').astype(str))
        else:
            mo_ends=list(pd.date_range(start=start_mo, end=str(datetime.now().year+1)+'-01', freq='M').astype(str))
    else:
        if end_mo.split('-')[1] != '12':
            mo_ends=list(pd.date_range(start=start_mo, end=end_mo.split('-')[0]+'-'+str(int(end_mo.split('-')[1])+1), freq='M').astype(str))
        else:
            mo_ends=list(pd.date_range(start=start_mo, end=str(int(end_mo.split('-')[0])+1)+'-01', freq='M').astype(str))
    mo_starts=[]
    for i in mo_ends:
        mo_starts.append(i.split('-')[0]+'-'+i.split('-')[1]+'-01')
    datestrs=[list(x) for x in zip(mo_starts, mo_ends)]

    datetimes=[]
    for i in datestrs:
        datetimes.append([date(int(i[0].split('-')[0]),int(i[0].split('-')[1]),int(i[0].split('-')[2])), date(int(i[1].split('-')[0]),int(i[1].split('-')[1]),int(i[1].split('-')[2]))])

    months=[]
    for i in mo_ends:
        months.append([i.split('-')[0]+'-'+i.split('-')[1]])

    dateli=[a + b +c for a, b, c in zip(datestrs, datetimes,months)]

    return dateli


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

    return df


metrics=metrics_df()
metrics.to_csv('metrics.csv') # generate metrics csv
pct_growth_monthly=metrics.pct_change(axis='columns') # percentages are in fraction form, not multiplied by 100
pct_growth_yoy=metrics.pct_change(axis='columns',periods=12).dropna(axis=1,how='all') # percentages are in fraction form, not multiplied by 100
pct_growth_monthly.to_csv('pct_growth_monthly.csv')
pct_growth_yoy.to_csv('pct_growth_yoy.csv')
