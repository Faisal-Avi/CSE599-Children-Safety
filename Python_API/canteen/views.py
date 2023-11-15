# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse

# Create your views here.

import cx_Oracle
import json
import datetime

def get_connection_info_group():
    with open("C:\\db_connect_info\\group\\db_connection.txt") as f:
        conn_info = f.readlines()
    conn_info = [x.strip() for x in conn_info]
    return conn_info

def get_connection_info_food():
    with open("C:\\db_connect_info\\food\\db_connection.txt") as f:
        conn_info = f.readlines()
    conn_info = [x.strip() for x in conn_info]
    return conn_info

def get_connection_info_accessories():
    with open("C:\\db_connect_info\\accessories\\db_connection.txt") as f:
        conn_info = f.readlines()
    conn_info = [x.strip() for x in conn_info]
    return conn_info

def get_connection_info_dev():
    with open("C:\\db_connect_info\\dev\\db_connection.txt") as f:
        conn_info = f.readlines()
    conn_info = [x.strip() for x in conn_info]
    return conn_info

def query_db(query, args=(), one=False):
    list_conn_info = get_connection_info_group()
    db_connection_info = str(list_conn_info[0])
    con = cx_Oracle.connect(db_connection_info)
    cur_oracle = con.cursor()
    cur_oracle.execute(query, args)
    r = [dict((cur_oracle.description[i][0], value) \
              for i, value in enumerate(row)) for row in cur_oracle.fetchall()]
    cur_oracle.connection.close()
    return (r[0] if r else None) if one else r

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

############################################################################################# CANTEEN

def canteen_today(request):
    oracle_sql = '''SELECT hed.auto_formated_id,
                           ctd.lunch_type,
                           TO_CHAR(ctd.lunch_date,'DD-MON-RRRR') lunch_date,
                           hed.company sbu,
                           hed.dept_name,
                           NVL(ctd.meal_eaten, 0) meal_eaten
                    FROM can_token ct,
                         can_token_detail ctd,
                         hrm_employee_detail hed
                    WHERE ct.id = ctd.master_id(+)
                    AND hed.employee_id = ct.employee_id(+)
                    AND TRUNC(ctd.lunch_date) = TRUNC(SYSDATE)
                    AND ct.reference_name = 'GROUP'
                    UNION ALL
                    SELECT hed.auto_formated_id,
                           ctd.lunch_type,
                           TO_CHAR(ctd.lunch_date,'DD-MON-RRRR') lunch_date,
                           hed.company sbu,
                           hed.dept_name,
                           NVL(ctd.meal_eaten, 0) meal_eaten
                    FROM can_token ct,
                         can_token_detail ctd,
                         hrm_employee_detail@dblink_food hed
                    WHERE ct.id = ctd.master_id(+)
                    AND hed.employee_id = ct.employee_id(+)
                    AND TRUNC(ctd.lunch_date) = TRUNC(SYSDATE)
                    AND ct.reference_name = 'FOOD'
                    UNION ALL
                    SELECT hed.auto_formated_id,
                           ctd.lunch_type,
                           TO_CHAR(ctd.lunch_date,'DD-MON-RRRR') lunch_date,
                           hed.company sbu,
                           hed.dept_name,
                           NVL(ctd.meal_eaten, 0) meal_eaten
                    FROM can_token ct,
                         can_token_detail ctd,
                         hrm_employee_detail@dblink_accs hed
                    WHERE ct.id = ctd.master_id(+)
                    AND hed.employee_id = ct.employee_id(+)
                    AND TRUNC(ctd.lunch_date) = TRUNC(SYSDATE)
                    AND ct.reference_name IN ('ACCESSORIES','DLLL')'''
    my_query = query_db(oracle_sql)
    json_output = json.dumps(my_query)
    return HttpResponse(json_output)

def get_canteen_today_meal(request):
    if request.method == 'GET':
        oracle_sql = '''SELECT ctd.lunch_type
                        FROM can_token ct,
                             can_token_detail ctd,
                             hrm_employee_detail hed
                        WHERE ct.id = ctd.master_id(+)
                        AND ct.employee_id = hed.employee_id(+)
                        AND TRUNC(ctd.lunch_date) = TRUNC(SYSDATE)
                        AND ct.reference_name = 'GROUP'
                        AND hed.auto_formated_id = :employee_office_id
                        UNION
                        SELECT ctd.lunch_type
                        FROM can_token ct,
                             can_token_detail ctd,
                             hrm_employee_detail@dblink_food hed
                        WHERE ct.id = ctd.master_id(+)
                        AND ct.employee_id = hed.employee_id(+)
                        AND TRUNC(ctd.lunch_date) = TRUNC(SYSDATE)
                        AND ct.reference_name = 'FOOD'
                        AND hed.auto_formated_id = :employee_office_id
                        UNION
                        SELECT ctd.lunch_type
                        FROM can_token ct,
                             can_token_detail ctd,
                             hrm_employee_detail@dblink_accs hed
                        WHERE ct.id = ctd.master_id(+)
                        AND ct.employee_id = hed.employee_id(+)
                        AND TRUNC(ctd.lunch_date) = TRUNC(SYSDATE)
                        AND ct.reference_name IN ('ACCESSORIES','DLLL')
                        AND hed.auto_formated_id = :employee_office_id'''
        l_data = request.GET
        l_dic = l_data.dict()
        l_employee_office_id = l_dic["employee_office_id"]
        my_query = query_db(oracle_sql, {'employee_office_id': l_employee_office_id})
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

def upd_can_token_detail(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        l_emp_id = l_dic["employee_office_id"]
        cur_oracle.callproc("front_end_support_tool.upd_can_detail_token",[l_emp_id])
        con.commit()
        return HttpResponse(True)
        
def is_meal_eaten(request):
    if request.method == 'GET':
        oracle_sql = '''SELECT NVL(ctd.meal_eaten,0) meal_eaten,
                               NVL(ctd.is_active,0) is_canceled
                        FROM can_token ct,
                             can_token_detail ctd,
                             hrm_employee_detail hed
                        WHERE ct.id = ctd.master_id(+)
                        AND ct.employee_id = hed.employee_id(+)
                        AND TRUNC(ctd.lunch_date) = TRUNC(SYSDATE)
                        AND ct.reference_name = 'GROUP'
                        AND hed.auto_formated_id = :employee_office_id
                        UNION
                        SELECT NVL(ctd.meal_eaten,0) meal_eaten,
                               NVL(ctd.is_active,0) is_canceled
                        FROM can_token ct,
                             can_token_detail ctd,
                             hrm_employee_detail@dblink_food hed
                        WHERE ct.id = ctd.master_id(+)
                        AND ct.employee_id = hed.employee_id(+)
                        AND TRUNC(ctd.lunch_date) = TRUNC(SYSDATE)
                        AND ct.reference_name = 'FOOD'
                        AND hed.auto_formated_id = :employee_office_id
                        UNION
                        SELECT NVL(ctd.meal_eaten,0) meal_eaten,
                               NVL(ctd.is_active,0) is_canceled
                        FROM can_token ct,
                             can_token_detail ctd,
                             hrm_employee_detail@dblink_accs hed
                        WHERE ct.id = ctd.master_id(+)
                        AND ct.employee_id = hed.employee_id(+)
                        AND TRUNC(ctd.lunch_date) = TRUNC(SYSDATE)
                        AND ct.reference_name IN ('ACCESSORIES','DLLL')
                        AND hed.auto_formated_id = :employee_office_id'''
        l_data = request.GET
        l_dic = l_data.dict()
        l_employee_office_id = l_dic["employee_office_id"]
        my_query = query_db(oracle_sql, {'employee_office_id': l_employee_office_id})
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)