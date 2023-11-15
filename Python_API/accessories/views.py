# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse

# Create your views here.

import cx_Oracle
import json
import datetime

###################################################################  DB connection and Static Functions

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
    try:
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        cur_oracle.execute(query, args)
        r = [dict((cur_oracle.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cur_oracle.fetchall()]
        cur_oracle.connection.close()
        return (r[0] if r else None) if one else r
    except:
        pass

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

######################################################################### Login and Privileges

def user_authentication(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_user_name = l_dic["user_name"]
        l_pass_word = l_dic["pass_word"]
        l_reference = l_dic["reference"]
        l_list_of_tuples = l_dic.items() #Dictionary to list of tuples
        l_result = cur_oracle.callfunc('front_end_support_tool.check_login_credential', cx_Oracle.NUMBER, (l_user_name, l_pass_word, l_reference))
        l_emp_id = cur_oracle.callfunc('front_end_support_tool.get_emp_id', cx_Oracle.NUMBER, (l_user_name, l_pass_word, l_reference))
        l_employee_office_id = cur_oracle.callfunc('front_end_support_tool.get_employee_office_id', cx_Oracle.STRING, (l_user_name, l_pass_word))
        print(l_result)
        print(l_employee_office_id)
        con.commit()
        l_authentication_result = {"authentication_result":l_result , "employee_office_id":l_employee_office_id, "employee_ref_id":int(l_emp_id)}
        l_json_output_1 = json.dumps(l_authentication_result)
        return HttpResponse(l_json_output_1)

def user_priv(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_emp_id = l_dic["employee_id"]
        l_object_access = cur_oracle.callfunc('front_end_support_tool.check_object_access', cx_Oracle.STRING,(l_emp_id, 'allSBU', 'A'))
        oracle_sql_1 = '''SELECT sbu
                        FROM
                        (
                            SELECT gc.short_name sbu,
                                   he.auto_formated_id,
                                   gc.display_serial
                            FROM user_units uu,
                                 gbl_company gc,
                                 hrm_employee_detail he
                            WHERE uu.user_id = he.employee_id
                            AND uu.unit_dept_no = gc.company_id
                            UNION ALL
                            SELECT gc.short_name sbu,
                                   he.auto_formated_id,
                                   gc.display_serial
                            FROM user_units@dblink_food uu,
                                 gbl_company@dblink_food gc,
                                 hrm_employee_detail@dblink_food he
                            WHERE uu.user_id = he.employee_id
                            AND uu.unit_dept_no = gc.company_id
                            UNION ALL
                            SELECT gc.short_name sbu,
                                   he.auto_formated_id,
                                   gc.display_serial
                            FROM user_units@dblink_accs uu,
                                 gbl_company@dblink_accs gc,
                                 hrm_employee_detail@dblink_accs he
                            WHERE uu.user_id = he.employee_id
                            AND uu.unit_dept_no = gc.company_id
                        )
                        WHERE auto_formated_id = :id
                        ORDER BY display_serial'''
        oracle_sql_2 = '''SELECT DISTINCT sbu
                          FROM
                          (
                                SELECT gc.short_name sbu , 'GROUP' ref
                                FROM  gbl_company gc
                                UNION ALL
                                SELECT gc.short_name sbu , 'FOOD' ref 
                                FROM gbl_company@dblink_food gc
                                UNION ALL
                                SELECT gc.short_name sbu , 'ACCESSORIES' ref
                                FROM gbl_company@dblink_accs gc
                          )'''
        if l_object_access == 'Y':
            my_query = query_db(oracle_sql_2)
        else:
            my_query = query_db(oracle_sql_1, {'id': l_emp_id})
        l_json_output_2 = json.dumps(my_query)
        return HttpResponse(l_json_output_2)

def emp_info(request):
    oracle_sql = '''SELECT *
                    FROM employee_info_pabx_v'''
    my_query = query_db(oracle_sql)
    json_output = json.dumps(my_query)
    return HttpResponse(json_output)

def sbu_wise_dept(request):
    oracle_sql = '''SELECT DISTINCT sbu_short_form, TO_CHAR(WM_CONCAT(DISTINCT dept_name)) sbu_wise_dept
    				FROM employee_info_pabx_v
    				GROUP BY sbu_short_form
    				UNION ALL
    				SELECT 'ALL' sub_short_form , TO_CHAR(WM_CONCAT(DISTINCT dept_name)) sbu_wise_dept
    				FROM employee_info_pabx_v'''
    my_query = query_db(oracle_sql)
    json_output = json.dumps(my_query)
    return HttpResponse(json_output)

def sbu(request):
    oracle_sql = '''SELECT DISTINCT sbu_short_form
                    FROM employee_info_pabx_v'''
    my_query = query_db(oracle_sql)
    json_output = json.dumps(my_query)
    return HttpResponse(json_output)

def dept_name(request):
    oracle_sql = '''SELECT DISTINCT dept_name
                    FROM employee_info_pabx_v'''
    my_query = query_db(oracle_sql)
    json_output = json.dumps(my_query)
    return HttpResponse(json_output)