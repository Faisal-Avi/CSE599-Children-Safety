# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse

# Create your views here.

import cx_Oracle
import sys
import json
import time

db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
con = cx_Oracle.connect(db_connection_info)

oracle_sql = '''SELECT DISTINCT sbu_short_form, TO_CHAR(WM_CONCAT(DISTINCT dept_name)) sbu_wise_dept
				FROM employee_info_pabx_v
				GROUP BY sbu_short_form
				UNION ALL
				SELECT 'ALL' sub_short_form , TO_CHAR(WM_CONCAT(DISTINCT dept_name)) sbu_wise_dept
				FROM employee_info_pabx_v'''                      
cur_oracle = con.cursor()                
cur_oracle.execute(oracle_sql);
l_list = cur_oracle.fetchall()

def query_db(query, args=(), one=False):
    db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
    con = cx_Oracle.connect(db_connection_info)
    cur_oracle = con.cursor()
    cur_oracle.execute(query, args)
    r = [dict((cur_oracle.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur_oracle.fetchall()]
    cur_oracle.connection.close()
    return (r[0] if r else None) if one else r

def sbu_wise_dept(request):
	my_query = query_db(oracle_sql)
	json_output = json.dumps(my_query)
	return HttpResponse(json_output)   