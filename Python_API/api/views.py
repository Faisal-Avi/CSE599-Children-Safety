# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse

# Create your views here.

import cx_Oracle
import json
import datetime
from django.views import View

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
        l_emp_id = cur_oracle.callfunc('front_end_support_tool.get_emp_id', cx_Oracle.NUMBER, (l_user_name, l_pass_word))
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
                    FROM employee_info_pabx_v
                    ORDER BY 1'''
    my_query = query_db(oracle_sql)
    json_output = json.dumps(my_query)
    return HttpResponse(json_output)

############################################################# Attendance

def late_att_list(request):
    if request.method == 'GET':
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        l_month_year = l_dic["month_year"]
        l_late_count = l_dic["late_count"]
        oracle_sql = '''SELECT DENSE_RANK() OVER(PARTITION BY dept_name ORDER BY dept_name, display_serial, employee_full_name) sl,
                               employee_full_name,
                               desig_name,
                               auto_formated_id,
                               employee_id,
                               dept_name,
                               company sbu,
                               display_serial,
                               late_count,
                               reference
                        FROM 
                        (   SELECT DISTINCT hed.employee_full_name,
                                   hed.desig_name,
                                   hed.auto_formated_id,
                                   hed.employee_id,
                                   hed.dept_name,
                                   hed.company,
                                   hed.display_serial,
                                   SUM(
                                         CASE
                                             WHEN hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN 
                                                  1 
                                             ELSE 0 
                                         END
                                     ) OVER(PARTITION BY hed.employee_id) late_count,
                                   'GROUP' reference
                            FROM hrm_employee_detail hed,
                                 (SELECT *
                                 FROM hrm_duty_roster hdr
                                 WHERE TO_CHAR(hdr.duty_date,'MMRRRR') = TO_CHAR(TO_DATE(:p_month_year),'MMRRRR')
                                 AND hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| '16','ddmmrrhh24mi')) hdr,
                                 hrm_shift hs
                            WHERE hed.employee_id = hdr.employee_id(+)
                            AND hdr.shift_id = hs.shift_id(+)
                            AND hed.employment_end_date IS NULL
                            AND hed.employee_category_id = 4041
                            AND hed.company_id IN (1,13)
                            AND hed.active_ind = 'Y'
                            UNION ALL
                            SELECT DISTINCT hed.employee_full_name,
                                   hed.desig_name,
                                   hed.auto_formated_id,
                                   hed.employee_id,
                                   hed.dept_name,
                                   hed.company,
                                   hed.display_serial,
                                   SUM(
                                         CASE
                                             WHEN hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN 
                                                  1 
                                             ELSE 0 
                                         END
                                     ) OVER(PARTITION BY hed.employee_id) late_count,
                                   'FOOD' reference
                            FROM hrm_employee_detail@dblink_food hed,
                                 (SELECT *
                                 FROM hrm_duty_roster@dblink_food hdr
                                 WHERE TO_CHAR(hdr.duty_date,'MMRRRR') = TO_CHAR(TO_DATE(:p_month_year),'MMRRRR') 
                                 AND hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| '16','ddmmrrhh24mi')) hdr,
                                 hrm_shift@dblink_food hs
                            WHERE hed.employee_id = hdr.employee_id(+)
                            AND hdr.shift_id = hs.shift_id(+)
                            AND hed.employment_end_date IS NULL
                            AND hed.employee_category_id = 4041
                            AND hed.company_id = 1
                            AND hed.active_ind = 'Y'
                            UNION ALL
                            SELECT DISTINCT hed.employee_full_name,
                                   hed.desig_name,
                                   hed.auto_formated_id,
                                   hed.employee_id,
                                   hed.dept_name,
                                   hed.company,
                                   hed.display_serial,
                                   SUM(
                                         CASE
                                             WHEN hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN 
                                                  1 
                                             ELSE 0 
                                         END
                                     ) OVER(PARTITION BY hed.employee_id) late_count,
                                   'ACCESSORIES' reference
                            FROM hrm_employee_detail@dblink_accs hed,
                                 (SELECT *
                                 FROM hrm_duty_roster@dblink_accs hdr
                                 WHERE TO_CHAR(hdr.duty_date,'MMRRRR') = TO_CHAR(TO_DATE(:p_month_year),'MMRRRR') 
                                 AND hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| '16','ddmmrrhh24mi')) hdr,
                                 hrm_shift@dblink_accs hs
                            WHERE hed.employee_id = hdr.employee_id(+)
                            AND hdr.shift_id = hs.shift_id(+)
                            AND hed.employment_end_date IS NULL
                            AND hed.employee_category_id = 4041
                            AND hed.company_id IN (1, 2, 5)
                            AND hed.active_ind = 'Y'
                        )    
                        WHERE late_count >= NVL(:p_late_count,1)
                        ORDER BY late_count DESC'''
        my_query = query_db(oracle_sql,{'p_month_year':l_month_year, 'p_late_count':l_late_count})
        json_output = json.dumps(my_query)
        return HttpResponse(json_output)

def late_att_list_detail(request):
    if request.method == 'GET':
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        l_month_year = l_dic["month_year"]
        l_employee_id = l_dic["employee_id"]
        l_reference = l_dic["reference"]
        oracle_sql = '''SELECT employee_id,
                               TO_CHAR(duty_date, 'DD-MM-RR') duty_date,
                               TO_CHAR(in_dttm, 'HH:MI AM') in_dttm,
                               TO_CHAR(out_dttm, 'HH:MI AM') out_dttm
                        FROM 
                        (   SELECT DISTINCT hed.employee_full_name,
                                   hed.desig_name,
                                   hed.auto_formated_id,
                                   hed.employee_id,
                                   hed.dept_name,
                                   hed.company,
                                   hed.display_serial,
                                   hdr.duty_date,
                                   hdr.in_dttm,
                                   hdr.out_dttm,
                                   'GROUP' reference
                            FROM hrm_employee_detail hed,
                                 (SELECT *
                                 FROM hrm_duty_roster hdr
                                 WHERE TO_CHAR(hdr.duty_date,'MMRRRR') = TO_CHAR(TO_DATE(:p_month_year),'MMRRRR')
                                 AND hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| '16','ddmmrrhh24mi')) hdr,
                                 hrm_shift hs
                            WHERE hed.employee_id = hdr.employee_id(+)
                            AND hdr.shift_id = hs.shift_id(+)
                            AND hed.employment_end_date IS NULL
                            AND hed.employee_category_id = 4041
                            AND hed.company_id IN (1,13)
                            AND hed.active_ind = 'Y'
                            UNION ALL
                            SELECT DISTINCT hed.employee_full_name,
                                   hed.desig_name,
                                   hed.auto_formated_id,
                                   hed.employee_id,
                                   hed.dept_name,
                                   hed.company,
                                   hed.display_serial,
                                   hdr.duty_date,
                                   hdr.in_dttm,
                                   hdr.out_dttm,
                                   'FOOD' reference
                            FROM hrm_employee_detail@dblink_food hed,
                                 (SELECT *
                                 FROM hrm_duty_roster@dblink_food hdr
                                 WHERE TO_CHAR(hdr.duty_date,'MMRRRR') = TO_CHAR(TO_DATE(:p_month_year),'MMRRRR')
                                 AND hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| '16','ddmmrrhh24mi')) hdr,
                                 hrm_shift@dblink_food hs
                            WHERE hed.employee_id = hdr.employee_id(+)
                            AND hdr.shift_id = hs.shift_id(+)
                            AND hed.employment_end_date IS NULL
                            AND hed.employee_category_id = 4041
                            AND hed.company_id = 1
                            AND hed.active_ind = 'Y'
                            UNION ALL
                            SELECT DISTINCT hed.employee_full_name,
                                   hed.desig_name,
                                   hed.auto_formated_id,
                                   hed.employee_id,
                                   hed.dept_name,
                                   hed.company,
                                   hed.display_serial,
                                   hdr.duty_date,
                                   hdr.in_dttm,
                                   hdr.out_dttm,
                                   'ACCESSORIES' reference
                            FROM hrm_employee_detail@dblink_accs hed,
                                 (SELECT *
                                 FROM hrm_duty_roster@dblink_accs hdr
                                 WHERE TO_CHAR(hdr.duty_date,'MMRRRR') = TO_CHAR(TO_DATE(:p_month_year),'MMRRRR')
                                 AND hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| '16','ddmmrrhh24mi')) hdr,
                                 hrm_shift@dblink_accs hs
                            WHERE hed.employee_id = hdr.employee_id(+)
                            AND hdr.shift_id = hs.shift_id(+)
                            AND hed.employment_end_date IS NULL
                            AND hed.employee_category_id = 4041
                            AND hed.company_id IN (1, 2, 5)
                            AND hed.active_ind = 'Y'
                        )    
                        WHERE employee_id = :p_employee_id
                        AND reference = :p_reference'''
        my_query = query_db(oracle_sql,{'p_month_year':l_month_year, 'p_employee_id':l_employee_id, 'p_reference':l_reference})
        json_output = json.dumps(my_query, default=myconverter)
        return HttpResponse(json_output)

def attendance(request):
    oracle_sql = '''SELECT  *
                   FROM hrm_attendance_info'''
    my_query = query_db(oracle_sql)
    json_output = json.dumps(my_query)
    return HttpResponse(json_output)

def job_card_rpt(request):
    if request.method == 'GET':
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_emp_id = l_dic["employee_id"]
        oracle_sql = '''SELECT employee_id,
                               joining_date,
                               duration,
                               duty_date,
                               duty_date_full,
                               duty_day,
                               in_time,
                               out_time,
                               late_min,
                               late,
                               day_status
                        FROM       
                            (
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'DD-Mon-RRRR') duty_date_full,
                                       TO_CHAR(hdr.duty_date, 'Dy') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                             NULL
                                       END late,
                                       CASE
                                        WHEN get_employee_day_type (
                                               hed.company_id,
                                               hdr.duty_date,
                                               hed.employee_id) = 'Y'
                                       THEN
                                          CASE
                                             WHEN hrm_payroll.chk_half_day_leave (
                                                     hed.employee_id,
                                                     hdr.duty_date) = 'N'
                                             THEN
                                                CASE
                                                   WHEN hdr.in_dttm <=
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'P'
                                                   WHEN hdr.in_dttm >
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'L'
                                                   WHEN hdr.in_dttm IS NULL AND hdr.out_dttm IS NULL
                                                   THEN
                                                      CASE
                                                         WHEN hrm_payroll.check_recom_leave_date (
                                                                 hed.employee_id,
                                                                 hdr.duty_date) = 'Y'
                                                         THEN
                                                            hrm_payroll.get_leave_type (
                                                               hed.employee_id,
                                                               hdr.duty_date)
                                                         WHEN hdr.shift_id IS NULL
                                                         THEN
                                                            NULL
                                                         WHEN hdr.shift_id IS NOT NULL AND TRUNC(hdr.duty_date) <= TRUNC(SYSDATE) THEN
                                                            'A'
                                                      END
                                                END
                                             ELSE
                                                hrm_payroll.get_leave_type (
                                                   hed.employee_id,
                                                   hdr.duty_date)
                                          END
                                       ELSE
                                          CASE
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'W'
                                             THEN
                                                'PW'
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'H'
                                             THEN
                                                'PH'
                                             WHEN hdr.in_dttm IS NULL
                                             THEN
                                                get_employee_day_type (
                                                   hed.company_id,
                                                   hdr.duty_date,
                                                   hed.employee_id)
                                          END
                                       END day_status
                                FROM hrm_duty_roster hdr,
                                     hrm_employee_detail hed,
                                     hrm_shift hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(SYSDATE, 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                                UNION ALL
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'DD-Mon-RRRR') duty_date_full,
                                       TO_CHAR(hdr.duty_date, 'Day') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                             NULL
                                       END late,
                                       CASE
                                        WHEN get_employee_day_type (
                                               hed.company_id,
                                               hdr.duty_date,
                                               hed.employee_id) = 'Y'
                                       THEN
                                          CASE
                                             WHEN hrm_payroll.chk_half_day_leave (
                                                     hed.employee_id,
                                                     hdr.duty_date) = 'N'
                                             THEN
                                                CASE
                                                   WHEN hdr.in_dttm <=
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'P'
                                                   WHEN hdr.in_dttm >
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'L'
                                                   WHEN hdr.in_dttm IS NULL AND hdr.out_dttm IS NULL
                                                   THEN
                                                      CASE
                                                         WHEN hrm_payroll.check_recom_leave_date (
                                                                 hed.employee_id,
                                                                 hdr.duty_date) = 'Y'
                                                         THEN
                                                            hrm_payroll.get_leave_type (
                                                               hed.employee_id,
                                                               hdr.duty_date)
                                                         WHEN hdr.shift_id IS NULL
                                                         THEN
                                                            NULL
                                                         WHEN hdr.shift_id IS NOT NULL AND TRUNC(hdr.duty_date) <= TRUNC(SYSDATE) THEN 'A'
                                                      END
                                                END
                                             ELSE
                                                hrm_payroll.get_leave_type (
                                                   hed.employee_id,
                                                   hdr.duty_date)
                                          END
                                       ELSE
                                          CASE
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'W'
                                             THEN
                                                'PW'
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'H'
                                             THEN
                                                'PH'
                                             WHEN hdr.in_dttm IS NULL
                                             THEN
                                                get_employee_day_type (
                                                   hed.company_id,
                                                   hdr.duty_date,
                                                   hed.employee_id)
                                          END
                                       END day_status
                                FROM hrm_duty_roster@dblink_food hdr,
                                     hrm_employee_detail@dblink_food hed,
                                     hrm_shift@dblink_food hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(SYSDATE, 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                                UNION ALL
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'DD-Mon-RRRR') duty_date_full,
                                       TO_CHAR(hdr.duty_date, 'Day') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                              NULL
                                       END late,
                                       CASE
                                        WHEN get_employee_day_type (
                                               hed.company_id,
                                               hdr.duty_date,
                                               hed.employee_id) = 'Y'
                                       THEN
                                          CASE
                                             WHEN hrm_payroll.chk_half_day_leave (
                                                     hed.employee_id,
                                                     hdr.duty_date) = 'N'
                                             THEN
                                                CASE
                                                   WHEN hdr.in_dttm <=
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'P'
                                                   WHEN hdr.in_dttm >
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'L'
                                                   WHEN hdr.in_dttm IS NULL AND hdr.out_dttm IS NULL
                                                   THEN
                                                      CASE
                                                         WHEN hrm_payroll.check_recom_leave_date (
                                                                 hed.employee_id,
                                                                 hdr.duty_date) = 'Y'
                                                         THEN
                                                            hrm_payroll.get_leave_type (
                                                               hed.employee_id,
                                                               hdr.duty_date)
                                                         WHEN hdr.shift_id IS NULL
                                                         THEN
                                                            NULL
                                                         WHEN hdr.shift_id IS NOT NULL AND TRUNC(hdr.duty_date) <= TRUNC(SYSDATE) THEN
                                                         'A'
                                                      END
                                                END
                                             ELSE
                                                hrm_payroll.get_leave_type (
                                                   hed.employee_id,
                                                   hdr.duty_date)
                                          END
                                       ELSE
                                          CASE
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'W'
                                             THEN
                                                'PW'
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'H'
                                             THEN
                                                'PH'
                                             WHEN hdr.in_dttm IS NULL
                                             THEN
                                                get_employee_day_type (
                                                   hed.company_id,
                                                   hdr.duty_date,
                                                   hed.employee_id)
                                          END
                                       END day_status
                                FROM hrm_duty_roster@dblink_accs hdr,
                                     hrm_employee_detail@dblink_accs hed,
                                     hrm_shift@dblink_accs hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(SYSDATE, 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                            )
                        WHERE employee_id = :employee_id
                        ORDER BY duty_date'''
        my_query = query_db(oracle_sql, {'employee_id': l_emp_id} )
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

def job_card_rpt_self(request):
    if request.method == 'GET':
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_emp_id = l_dic["employee_id"]
        oracle_sql = '''SELECT employee_id,
                               joining_date,
                               duration,
                               duty_date,
                               duty_date_full,
                               duty_day,
                               in_time,
                               out_time,
                               late_min,
                               late,
                               day_status
                        FROM       
                            (
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'DD-Mon-RRRR') duty_date_full,
                                       TO_CHAR(hdr.duty_date, 'Dy') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                             NULL
                                       END late,
                                       CASE
                                        WHEN get_employee_day_type (
                                               hed.company_id,
                                               hdr.duty_date,
                                               hed.employee_id) = 'Y'
                                       THEN
                                          CASE
                                             WHEN hrm_payroll.chk_half_day_leave (
                                                     hed.employee_id,
                                                     hdr.duty_date) = 'N'
                                             THEN
                                                CASE
                                                   WHEN hdr.in_dttm <=
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'P'
                                                   WHEN hdr.in_dttm >
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'L'
                                                   WHEN hdr.in_dttm IS NULL AND hdr.out_dttm IS NULL
                                                   THEN
                                                      CASE
                                                         WHEN hrm_payroll.check_recom_leave_date (
                                                                 hed.employee_id,
                                                                 hdr.duty_date) = 'Y'
                                                         THEN
                                                            hrm_payroll.get_leave_type (
                                                               hed.employee_id,
                                                               hdr.duty_date)
                                                         WHEN hdr.shift_id IS NULL
                                                         THEN
                                                            NULL
                                                         WHEN hdr.shift_id IS NOT NULL AND TRUNC(hdr.duty_date) <= TRUNC(SYSDATE) THEN
                                                            'A'
                                                      END
                                                END
                                             ELSE
                                                hrm_payroll.get_leave_type (
                                                   hed.employee_id,
                                                   hdr.duty_date)
                                          END
                                       ELSE
                                          CASE
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'W'
                                             THEN
                                                'PW'
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'H'
                                             THEN
                                                'PH'
                                             WHEN hdr.in_dttm IS NULL
                                             THEN
                                                get_employee_day_type (
                                                   hed.company_id,
                                                   hdr.duty_date,
                                                   hed.employee_id)
                                          END
                                       END day_status
                                FROM hrm_duty_roster hdr,
                                     hrm_employee_detail hed,
                                     hrm_shift hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(SYSDATE, 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                                UNION ALL
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'DD-Mon-RRRR') duty_date_full,
                                       TO_CHAR(hdr.duty_date, 'Day') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                             NULL
                                       END late,
                                       CASE
                                        WHEN get_employee_day_type (
                                               hed.company_id,
                                               hdr.duty_date,
                                               hed.employee_id) = 'Y'
                                       THEN
                                          CASE
                                             WHEN hrm_payroll.chk_half_day_leave (
                                                     hed.employee_id,
                                                     hdr.duty_date) = 'N'
                                             THEN
                                                CASE
                                                   WHEN hdr.in_dttm <=
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'P'
                                                   WHEN hdr.in_dttm >
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'L'
                                                   WHEN hdr.in_dttm IS NULL AND hdr.out_dttm IS NULL
                                                   THEN
                                                      CASE
                                                         WHEN hrm_payroll.check_recom_leave_date (
                                                                 hed.employee_id,
                                                                 hdr.duty_date) = 'Y'
                                                         THEN
                                                            hrm_payroll.get_leave_type (
                                                               hed.employee_id,
                                                               hdr.duty_date)
                                                         WHEN hdr.shift_id IS NULL
                                                         THEN
                                                            NULL
                                                         WHEN hdr.shift_id IS NOT NULL AND TRUNC(hdr.duty_date) <= TRUNC(SYSDATE) THEN 'A'
                                                      END
                                                END
                                             ELSE
                                                hrm_payroll.get_leave_type (
                                                   hed.employee_id,
                                                   hdr.duty_date)
                                          END
                                       ELSE
                                          CASE
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'W'
                                             THEN
                                                'PW'
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'H'
                                             THEN
                                                'PH'
                                             WHEN hdr.in_dttm IS NULL
                                             THEN
                                                get_employee_day_type (
                                                   hed.company_id,
                                                   hdr.duty_date,
                                                   hed.employee_id)
                                          END
                                       END day_status
                                FROM hrm_duty_roster@dblink_food hdr,
                                     hrm_employee_detail@dblink_food hed,
                                     hrm_shift@dblink_food hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(SYSDATE, 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                                UNION ALL
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'DD-Mon-RRRR') duty_date_full,
                                       TO_CHAR(hdr.duty_date, 'Day') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                              NULL
                                       END late,
                                       CASE
                                        WHEN get_employee_day_type (
                                               hed.company_id,
                                               hdr.duty_date,
                                               hed.employee_id) = 'Y'
                                       THEN
                                          CASE
                                             WHEN hrm_payroll.chk_half_day_leave (
                                                     hed.employee_id,
                                                     hdr.duty_date) = 'N'
                                             THEN
                                                CASE
                                                   WHEN hdr.in_dttm <=
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'P'
                                                   WHEN hdr.in_dttm >
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'L'
                                                   WHEN hdr.in_dttm IS NULL AND hdr.out_dttm IS NULL
                                                   THEN
                                                      CASE
                                                         WHEN hrm_payroll.check_recom_leave_date (
                                                                 hed.employee_id,
                                                                 hdr.duty_date) = 'Y'
                                                         THEN
                                                            hrm_payroll.get_leave_type (
                                                               hed.employee_id,
                                                               hdr.duty_date)
                                                         WHEN hdr.shift_id IS NULL
                                                         THEN
                                                            NULL
                                                         WHEN hdr.shift_id IS NOT NULL AND TRUNC(hdr.duty_date) <= TRUNC(SYSDATE) THEN
                                                         'A'
                                                      END
                                                END
                                             ELSE
                                                hrm_payroll.get_leave_type (
                                                   hed.employee_id,
                                                   hdr.duty_date)
                                          END
                                       ELSE
                                          CASE
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'W'
                                             THEN
                                                'PW'
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'H'
                                             THEN
                                                'PH'
                                             WHEN hdr.in_dttm IS NULL
                                             THEN
                                                get_employee_day_type (
                                                   hed.company_id,
                                                   hdr.duty_date,
                                                   hed.employee_id)
                                          END
                                       END day_status
                                FROM hrm_duty_roster@dblink_accs hdr,
                                     hrm_employee_detail@dblink_accs hed,
                                     hrm_shift@dblink_accs hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(SYSDATE, 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                            )
                        WHERE employee_id = :employee_id
                        ORDER BY duty_date'''
        my_query = query_db(oracle_sql, {'employee_id': l_emp_id} )
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

####################################################################  Movement Log

def query_movement_register(request):
    if request.method == 'GET':
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_emp_id = l_dic["employee_id"]
        l_reference = l_dic["reference"]
        oracle_sql = '''SELECT movement_id,
                               employee_id,
                               TO_CHAR(movement_date , 'DD-MON-RRRR') movement_date,
                               out_dttm,
                               in_dttm,
                               location_from,
                               location_to,
                               purpose,
                               purpose_type,
                               reference
                        FROM hrm_movement_register
                        WHERE employee_id = :emp_id
                        AND reference = :ref
                     '''
        my_query = query_db(oracle_sql, {'emp_id': l_emp_id,'ref': l_reference})
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

def query_movement_register_all(request):
    if request.method == 'GET':
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_movement_date = l_dic["movement_date"]
        oracle_sql = '''SELECT movement_id,
                               employee_id,
                               TO_CHAR(movement_date , 'DD-MON-RRRR') movement_date,
                               out_dttm,
                               in_dttm,
                               location_from,
                               location_to,
                               purpose,
                               purpose_type,
                               reference
                        FROM hrm_movement_register
                        WHERE movement_date = :movement_date 
                     '''
        my_query = query_db(oracle_sql, {'movement_date': l_movement_date})
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

def ins_movement_register(request):
    if request.method == 'POST':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        l_emp_id = l_dic["employee_id"]
        l_movement_date = l_dic["movement_date"]
        l_out_dttm = l_dic["out_dttm"]
        l_in_dttm = l_dic["in_dttm"]
        l_location_from = l_dic["location_from"]
        l_location_to = l_dic["location_to"]
        l_purpose = l_dic["purpose"]
        cur_oracle.callproc("front_end_support_tool.ins_movement_register",
                  [l_emp_id,l_movement_date,l_out_dttm,l_in_dttm,l_location_from,l_location_to,l_purpose])
        con.commit()
        return HttpResponse(True)

def upd_movement_register(request):
    if request.method == 'POST':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_movement_id = l_dic["movement_id"]
        l_movement_date = l_dic["movement_date"]
        l_out_dttm = l_dic["out_dttm"]
        l_in_dttm = l_dic["in_dttm"]
        l_location_from = l_dic["location_from"]
        l_location_to = l_dic["location_to"]
        l_purpose = l_dic["purpose"]
        cur_oracle.callproc("front_end_support_tool.upd_movement_register",
                            [l_movement_id,l_movement_date,l_out_dttm,l_in_dttm,l_location_from,l_location_to,l_purpose])
        con.commit()
        return HttpResponse(True)

def del_movement_register(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_movement_id = l_dic["movement_id"]
        cur_oracle.callproc("front_end_support_tool.del_movement_register",
                            [l_movement_id])
        con.commit()
        return HttpResponse(True)

###############################################################################

##for getting office id card data

###############################################################################

class get_office_id_card_data(View):
    def get(self,request):
        if request.method == 'GET':
            l_data = request.GET
            l_dic = l_data.dict()
            for key in l_dic:
                l_employee_id = l_dic[key]
            oracle_sql = '''SELECT hed.employee_id,
                                  hed.employee_full_name,
                                  hed.auto_formated_id,
                                  hed.company,
                                  hed.desig_name,
                                  hed.dept_name,
                                  hed.joining_date,
                                  hed.blood_group,
                                  hed.permanent_address,
                                  hed.home_phone,
                                  hed.nin,
                                     'http://103.199.108.43/GROUP/EMPLOYEEPHOTO'
                                  || hed.employee_id
                                  || NVL (hr_admin_pack.get_max_attachment_sl (hed.employee_id), 1)
                                  || '.JPG'
                                     image_url,
                                  'GROUP' reference
                             FROM hrm_employee_detail hed
                             WHERE auto_formated_id = :p_auto_formated_id
                           UNION ALL
                           SELECT hed.employee_id,
                                  hed.employee_full_name,
                                  hed.auto_formated_id,
                                  hed.company,
                                  hed.desig_name,
                                  hed.dept_name,
                                  hed.joining_date,
                                  hed.blood_group,
                                  hed.permanent_address,
                                  hed.home_phone,
                                  hed.nin,
                                     'http://103.199.108.43/FOOD/EMPLOYEEPHOTO'
                                  || hed.employee_id
                                  || NVL (hr_admin_pack.get_max_attachment_sl (hed.employee_id), 1)
                                  || '.JPG'
                                     image_url,
                                  'FOOD' reference
                             FROM hrm_employee_detail@dblink_food hed
                             WHERE auto_formated_id = :p_auto_formated_id
                           UNION ALL
                           SELECT hed.employee_id,
                                  hed.employee_full_name,
                                  hed.auto_formated_id,
                                  hed.company,
                                  hed.desig_name,
                                  hed.dept_name,
                                  hed.joining_date,
                                  hed.blood_group,
                                  hed.permanent_address,
                                  hed.home_phone,
                                  hed.nin,
                                     'http://103.199.108.43/ACCESSORIES/EMPLOYEEPHOTO'
                                  || hed.employee_id
                                  || NVL (hr_admin_pack.get_max_attachment_sl (hed.employee_id), 1)
                                  || '.JPG'
                                     image_url,
                                  'ACCESSORIES' reference
                             FROM hrm_employee_detail@dblink_accs hed
                             WHERE auto_formated_id = :p_auto_formated_id'''
            my_query = query_db(oracle_sql, {'p_auto_formated_id': l_employee_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)
############################################################################################################## Version 2

def user_verification(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        l_user_name = l_dic["user_name"]
        l_pass_word = l_dic["pass_word"]
        l_result = cur_oracle.callfunc('front_end_support_tool.check_login_verification', cx_Oracle.NUMBER, (l_user_name, l_pass_word))
        l_emp_id = cur_oracle.callfunc('front_end_support_tool.get_emp_id', cx_Oracle.NUMBER, (l_user_name, l_pass_word))
        l_employee_office_id = cur_oracle.callfunc('front_end_support_tool.get_employee_office_id', cx_Oracle.STRING, (l_user_name, l_pass_word))
        l_employee_name = cur_oracle.callfunc('front_end_support_tool.get_employee_name', cx_Oracle.STRING, (l_user_name, l_pass_word))
        l_designation = cur_oracle.callfunc('front_end_support_tool.get_designation_name', cx_Oracle.STRING, (l_user_name, l_pass_word))
        l_dept = cur_oracle.callfunc('front_end_support_tool.get_department_name', cx_Oracle.STRING, (l_user_name, l_pass_word))
        l_url = cur_oracle.callfunc('front_end_support_tool.get_image_url', cx_Oracle.STRING, (l_user_name, l_pass_word))
        #print(l_result)
        #print(l_employee_office_id)
        con.commit()
        l_authentication_result = {
                                       "authentication_result": l_result ,
                                       "employee_office_id": l_employee_office_id,
                                       "employee_ref_id": int(l_emp_id),
                                       "employee_name" : l_employee_name,
                                       "designation" : l_designation,
                                       "department" : l_dept,
                                       "image_url" : l_url
                                  }
        l_json_output_1 = json.dumps(l_authentication_result)
        return HttpResponse(l_json_output_1)

def user_verify_from_emp_id(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        l_employee_id = l_dic["employee_id"]
        l_pass_word = l_dic["pass_word"]
        l_result = cur_oracle.callfunc('front_end_support_tool.check_login_from_emp_id', cx_Oracle.NUMBER, (l_employee_id,l_pass_word))
        l_emp_id = cur_oracle.callfunc('front_end_support_tool.get_emp_id', cx_Oracle.NUMBER, (l_employee_id,l_pass_word))
        l_employee_office_id = cur_oracle.callfunc('front_end_support_tool.get_employee_office_id', cx_Oracle.STRING, (l_employee_id,l_pass_word))
        l_employee_name = cur_oracle.callfunc('front_end_support_tool.get_emp_name', cx_Oracle.STRING, (l_employee_id,l_pass_word))
        l_designation = cur_oracle.callfunc('front_end_support_tool.get_desig_name', cx_Oracle.STRING, (l_employee_id,l_pass_word))
        l_dept = cur_oracle.callfunc('front_end_support_tool.get_dept_name', cx_Oracle.STRING, (l_employee_id,l_pass_word))
        #print(l_result)
        #print(l_employee_office_id)
        con.commit()
        l_authentication_result = {
                                       "authentication_result" : l_result ,
                                       "employee_office_id": l_employee_office_id,
                                       "employee_ref_id": int(l_emp_id),
                                       "employee_name" : l_employee_name,
                                       "designation" : l_designation,
                                       "department" : l_dept
                                  }
        l_json_output_1 = json.dumps(l_authentication_result)
        return HttpResponse(l_json_output_1)

def employee_information(request):
    if request.method == 'GET':
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        #l_employee_id = l_dic["employee_id"]
        oracle_sql = ''' SELECT NVL (phone_ext, 0) phone_ext,
                                NVL (known_name_in_office, employee_name) employee_name,
                                dept_name,
                                sbu,
                                sbu_short_form,
                                NVL (work_mobile, 0) work_mobile,
                                work_email,
                                employee_office_id,
                                desig_name,
                                image_url,
                                employee_id,
                                employee_name emp_name,
                                known_name_in_office
                           FROM (SELECT he.phone_ext,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 he.first_name
                                              || ' '
                                              || he.middle_name
                                              || ' '
                                              || he.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           employee_name,
                                        he.last_name short_name,
                                        gdept.dept_name,
                                        gc.company_name sbu,
                                        gc.short_name sbu_short_form,
                                        he.personal_mobile,
                                        he.work_mobile,
                                        he.personal_email,
                                        he.work_email,
                                        he.employee_id,
                                        he.auto_formated_id employee_office_id,
                                        gd.desig_name,
                                        gd.display_serial desig_rank,
                                        'GROUP' reference,
                                           'http://103.199.108.43/GROUP/EMPLOYEEPHOTO'
                                        || he.employee_id
                                        || NVL (
                                              hr_admin_pack.get_max_attachment_sl (he.employee_id),
                                              1)
                                        || '.JPG'
                                           image_url,
                                        he.known_name_in_office
                                   FROM hrm_employee he,
                                        gbl_dept gdept,
                                        gbl_desig gd,
                                        gbl_company gc
                                  WHERE     NVL (he.current_dept_id, he.joining_dept_id) =
                                               gdept.dept_id(+)
                                        AND NVL (he.current_desig_id, he.joining_desig_id) =
                                               gd.desig_id(+)
                                        AND NVL (he.current_company_id, he.joining_company_id) =
                                               gc.company_id(+)
                                        AND he.employee_category_id IN (4041, 4045)
                                        AND he.active_ind = 'Y'
                                        AND NVL (he.current_company_id, he.joining_company_id) IN
                                               (1, 13, 22, 23)
                                 UNION ALL
                                 SELECT he.phone_ext,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 he.first_name
                                              || ' '
                                              || he.middle_name
                                              || ' '
                                              || he.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           employee_name,
                                        he.last_name short_name,
                                        gdept.dept_name,
                                        gc.company_name sbu,
                                        gc.short_name sbu_short_form,
                                        he.personal_mobile,
                                        he.work_mobile,
                                        he.personal_email,
                                        he.work_email,
                                        he.employee_id,
                                        he.auto_formated_id employee_office_id,
                                        gd.desig_name,
                                        gd.display_serial desig_rank,
                                        'FOOD' reference,
                                           'http://103.199.108.43/FOOD/EMPLOYEEPHOTO'
                                        || he.employee_id
                                        || NVL (
                                              hr_admin_pack.get_max_attachment_sl@dblink_food (
                                                 he.employee_id),
                                              1)
                                        || '.JPG'
                                           image_url,
                                        he.known_name_in_office
                                   FROM hrm_employee@dblink_food he,
                                        gbl_dept@dblink_food gdept,
                                        gbl_desig@dblink_food gd,
                                        gbl_company@dblink_food gc
                                  WHERE     NVL (he.current_dept_id, he.joining_dept_id) =
                                               gdept.dept_id(+)
                                        AND NVL (he.current_desig_id, he.joining_desig_id) =
                                               gd.desig_id(+)
                                        AND NVL (he.current_company_id, he.joining_company_id) =
                                               gc.company_id(+)
                                        AND he.employee_category_id = 4041
                                        AND he.active_ind = 'Y'
                                        AND NVL (he.current_company_id, he.joining_company_id) = 1
                                 UNION ALL
                                 SELECT he.phone_ext,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 he.first_name
                                              || ' '
                                              || he.middle_name
                                              || ' '
                                              || he.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           employee_name,
                                        he.last_name short_name,
                                        gdept.dept_name,
                                        gc.company_name sbu,
                                        gc.short_name sbu_short_form,
                                        he.personal_mobile,
                                        he.work_mobile,
                                        he.personal_email,
                                        he.work_email,
                                        he.employee_id,
                                        he.auto_formated_id employee_office_id,
                                        TRIM (gd.desig_name) desig_name,
                                        gd.display_serial desig_rank,
                                        'ACCESSORIES' reference,
                                           'http://103.199.108.43/ACCESSORIES/EMPLOYEEPHOTO'
                                        || he.employee_id
                                        || NVL (
                                              hr_admin_pack.get_max_attachment_sl@dblink_accs (
                                                 he.employee_id),
                                              1)
                                        || '.JPG'
                                           image_url,
                                        he.known_name_in_office
                                   FROM hrm_employee@dblink_accs he,
                                        gbl_dept@dblink_accs gdept,
                                        gbl_desig@dblink_accs gd,
                                        gbl_company@dblink_accs gc
                                  WHERE     NVL (he.current_dept_id, he.joining_dept_id) =
                                               gdept.dept_id(+)
                                        AND NVL (he.current_desig_id, he.joining_desig_id) =
                                               gd.desig_id(+)
                                        AND NVL (he.current_company_id, he.joining_company_id) =
                                               gc.company_id(+)
                                        AND he.employee_category_id = 4041
                                        AND he.active_ind = 'Y'
                                        AND NVL (he.current_company_id, he.joining_company_id) IN
                                               (1, 2, 5))
                        ORDER BY desig_rank
        '''
        my_query = query_db(oracle_sql)
        json_output = json.dumps(my_query)
        return HttpResponse(json_output)

def attendance_information(request):
    if request.method == 'GET':
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        l_employee_id = l_dic["employee_id"]
        l_date = l_dic["p_date"]
        print(l_employee_id)
        print(l_date)
        oracle_sql = '''SELECT employee_full_name,
                               office_id employee_id,
                               image_url,
                               dept_name,
                               sbu,
                               duty_date,
                               in_dttm,
                               out_dttm,
                               leave_date,
                               day_status,
                               reference
                        FROM (SELECT REGEXP_REPLACE (
                                     TRIM (
                                           hed.first_name
                                        || ' '
                                        || hed.middle_name
                                        || ' '
                                        || hed.last_name
                                        || ' '),
                                     '[[:space:]]+',
                                     ' ') employee_full_name,
                                  hed.auto_formated_id office_id,
                                  hed.employee_id,
                                     'http://103.199.108.43/GROUP/EMPLOYEEPHOTO'
                                    || hed.employee_id
                                    || NVL (
                                          att.sl,
                                          1)
                                    || '.JPG'
                                       image_url,
                                  gd.dept_name,
                                  gdg.desig_name,
                                  gc.short_name sbu,
                                  hed.work_mobile,
                                  TO_CHAR (hdr.duty_date, 'DD/MM/RRRR') duty_date,
                                  TO_CHAR (hdr.in_dttm, 'HH24:MI') in_dttm,
                                  hdr.in_dttm in_time,
                                  TO_CHAR (hdr.out_dttm, 'HH24:MI') out_dttm,
                                  TO_CHAR (leave.application_dttm, 'DD/MM/RRRR') leave_date,
                                  CASE
                                     WHEN hdr.in_dttm IS NOT NULL OR hdr.out_dttm IS NOT NULL
                                     THEN
                                        CASE
                                           WHEN hdr.in_dttm >=
                                                   TO_DATE (
                                                         TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                      || '09'
                                                      || 1600,
                                                      'ddmmrrhh24miss')
                                           THEN
                                              'Present-Late'
                                           ELSE
                                              'Present-OnTime'
                                        END
                                     WHEN     hdr.in_dttm IS NULL
                                          AND hdr.out_dttm IS NULL
                                          AND leave.application_dttm IS NOT NULL
                                     THEN
                                        'Leave'
                                     WHEN     hdr.duty_date IS NOT NULL
                                          AND hdr.in_dttm IS NULL
                                          AND HDR.OUT_DTTM IS NULL
                                     THEN
                                        'Absent'
                                  END
                                     day_status,
                                  'GROUP' reference
                             FROM hrm_employee hed,
                                  gbl_dept gd,
                                  gbl_company gc,
                                  gbl_desig gdg,
                                  (SELECT MAX(display_serial) sl,
                                          ref_pk_column_value employee_id
                                FROM gbl_attachments
                                WHERE attachment_type_id = 1
                                GROUP BY ref_pk_column_value) att,                      
                                  (SELECT duty_date,
                                          in_dttm,
                                          out_dttm,
                                          employee_id
                                     FROM hrm_duty_roster
                                    WHERE duty_date =  :p_date) hdr,
                                  (SELECT hla.employee_id, hla.application_dttm
                                     FROM hrm_leave_application hla
                                    WHERE  :p_date BETWEEN TRUNC (hla.start_date)
                                                              AND TRUNC (hla.end_date)) leave
                            WHERE  hed.current_company_id = gc.company_id
                                  AND hed.current_dept_id = gd.dept_id
                                  AND hed.current_desig_id = gdg.desig_id
                                  AND hed.employee_id = hdr.employee_id
                                  AND hed.employee_id = att.employee_id(+)
                                  AND hed.employee_id = leave.employee_id(+)
                                  AND hed.employee_category_id = 4041
                                  AND hed.active_ind = 'Y'
                                  AND hed.current_company_id IN (1, 13)
                                  AND (
                                       hed.auto_formated_id = :employee_id
                                       OR hed.auto_formated_id IN  (SELECT hea.emp_auto_id FROM hrm_employee_authority hea WHERE hea.active_ind = 'Y' AND auth_emp_auto_id = :employee_id)
                        --               OR 'GROUP' = (SELECT soa.display_name FROM sec_objectaccess soa  WHERE soa.object_id = 1001  AND soa.auto_formated_id = :employee_id AND soa.active_ind = 'Y')
                                       OR 'AppsAllData' = (SELECT display_name FROM sec_objectaccess WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                                           UNION ALL
                                                           SELECT display_name FROM sec_objectaccess@dblink_food WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                                           UNION ALL
                                                           SELECT display_name FROM sec_objectaccess@dblink_accs WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y')
                        --               OR hed.auto_formated_id IN (SELECT allow_employee_auto_id FROM employee_allows WHERE employee_auto_id = :employee_id
                        --                                           UNION ALL
                        --                                           SELECT allow_employee_auto_id FROM employee_allows@dblink_food WHERE employee_auto_id = :employee_id
                        --                                           UNION ALL
                        --                                           SELECT allow_employee_auto_id FROM employee_allows@dblink_accs WHERE employee_auto_id = :employee_id)
                                       )
                           UNION ALL
                           SELECT REGEXP_REPLACE (
                                     TRIM (
                                           hed.first_name
                                        || ' '
                                        || hed.middle_name
                                        || ' '
                                        || hed.last_name
                                        || ' '),
                                     '[[:space:]]+',
                                     ' ') employee_full_name,
                                  hed.auto_formated_id office_id,
                                  hed.employee_id,
                                     'http://103.199.108.43/FOOD/EMPLOYEEPHOTO'
                                    || hed.employee_id
                                    || NVL (
                                          att.sl,
                                          1)
                                    || '.JPG'
                                       image_url,
                                  gd.dept_name,
                                  gdg.desig_name,
                                  gc.short_name sbu,
                                  hed.work_mobile,
                                  TO_CHAR (hdr.duty_date, 'DD/MM/RRRR') duty_date,
                                  TO_CHAR (hdr.in_dttm, 'HH24:MI') in_dttm,
                                  hdr.in_dttm in_time,
                                  TO_CHAR (hdr.out_dttm, 'HH24:MI') out_dttm,
                                  TO_CHAR (leave.application_dttm, 'DD/MM/RRRR') leave_date,
                                  CASE
                                     WHEN hdr.in_dttm IS NOT NULL OR hdr.out_dttm IS NOT NULL
                                     THEN
                                        CASE
                                           WHEN hdr.in_dttm >=
                                                   TO_DATE (
                                                         TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                      || '09'
                                                      || 1600,
                                                      'ddmmrrhh24miss')
                                           THEN
                                              'Present-Late'
                                           ELSE
                                              'Present-OnTime'
                                        END
                                     WHEN     hdr.in_dttm IS NULL
                                          AND hdr.out_dttm IS NULL
                                          AND leave.application_dttm IS NOT NULL
                                     THEN
                                        'Leave'
                                     WHEN     hdr.duty_date IS NOT NULL
                                          AND hdr.in_dttm IS NULL
                                          AND hdr.out_dttm IS NULL
                                     THEN
                                        'Absent'
                                  END
                                     day_status,
                                  'FOOD' reference
                             FROM hrm_employee@dblink_food hed,
                                  gbl_dept@dblink_food gd,
                                  gbl_company@dblink_food gc,
                                  gbl_desig@dblink_food gdg,
                                  (SELECT MAX(display_serial) sl,
                                          ref_pk_column_value employee_id
                                FROM gbl_attachments@dblink_food
                                WHERE attachment_type_id = 1
                                GROUP BY ref_pk_column_value) att,
                                  (SELECT duty_date,
                                          in_dttm,
                                          out_dttm,
                                          employee_id
                                     FROM hrm_duty_roster@dblink_food
                                    WHERE duty_date = :p_date) hdr,
                                  (SELECT hla.employee_id, hla.application_dttm
                                     FROM hrm_leave_application@dblink_food hla
                                    WHERE :p_date BETWEEN TRUNC (hla.start_date)
                                                              AND TRUNC (hla.end_date)) leave
                            WHERE  hed.current_company_id = gc.company_id
                                  AND hed.current_dept_id = gd.dept_id
                                  AND hed.current_desig_id = gdg.desig_id
                                  AND   hed.employee_id = hdr.employee_id
                                  AND hed.employee_id = att.employee_id(+)
                                  AND hed.employee_id = leave.employee_id(+)
                                  AND hed.employee_category_id = 4041
                                  AND hed.active_ind = 'Y'
                                  AND hed.current_company_id = 1
                                  AND (
                                       hed.auto_formated_id = :employee_id
                                       OR hed.auto_formated_id IN  (SELECT hea.emp_auto_id FROM hrm_employee_authority@dblink_food hea WHERE hea.active_ind = 'Y' AND auth_emp_auto_id = :employee_id)
                        --               OR 'FOOD' = (SELECT soa.display_name FROM sec_objectaccess@dblink_food soa  WHERE soa.object_id = 1001  AND soa.auto_formated_id = :employee_id AND soa.active_ind = 'Y')
                                       OR 'AppsAllData' = (SELECT display_name FROM sec_objectaccess WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                                           UNION ALL
                                                           SELECT display_name FROM sec_objectaccess@dblink_food WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                                           UNION ALL
                                                           SELECT display_name FROM sec_objectaccess@dblink_accs WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y')
                        --               OR hed.auto_formated_id IN (SELECT allow_employee_auto_id FROM employee_allows WHERE employee_auto_id = :employee_id
                        --                                           UNION ALL
                        --                                           SELECT allow_employee_auto_id FROM employee_allows@dblink_food WHERE employee_auto_id = :employee_id
                        --                                           UNION ALL
                        --                                           SELECT allow_employee_auto_id FROM employee_allows@dblink_accs WHERE employee_auto_id = :employee_id)
                                       )
                           UNION ALL
                           SELECT REGEXP_REPLACE (
                                     TRIM (
                                           hed.first_name
                                        || ' '
                                        || hed.middle_name
                                        || ' '
                                        || hed.last_name
                                        || ' '),
                                     '[[:space:]]+',
                                     ' ') employee_full_name,
                                  hed.auto_formated_id office_id,
                                  hed.employee_id,
                                     'http://103.199.108.43/ACCESSORIES/EMPLOYEEPHOTO'
                                    || hed.employee_id
                                    || NVL (
                                          att.sl,
                                          1)
                                    || '.JPG' image_url,
                                  gd.dept_name,
                                  gdg.desig_name,
                                  gc.short_name sbu,
                                  hed.work_mobile,
                                  TO_CHAR (hdr.duty_date, 'DD/MM/RRRR') duty_date,
                                  TO_CHAR (hdr.in_dttm, 'HH24:MI') in_dttm,
                                  hdr.in_dttm in_time,
                                  TO_CHAR (hdr.out_dttm, 'HH24:MI') out_dttm,
                                  TO_CHAR (leave.application_dttm, 'DD/MM/RRRR') leave_date,
                                  CASE
                                     WHEN hdr.in_dttm IS NOT NULL OR hdr.out_dttm IS NOT NULL
                                     THEN
                                        CASE
                                           WHEN hdr.in_dttm >=
                                                   TO_DATE (
                                                         TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                      || '09'
                                                      || 1600,
                                                      'ddmmrrhh24miss')
                                           THEN
                                              'Present-Late'
                                           ELSE
                                              'Present-OnTime'
                                        END
                                     WHEN     hdr.in_dttm IS NULL
                                          AND hdr.out_dttm IS NULL
                                          AND leave.application_dttm IS NOT NULL
                                     THEN
                                        'Leave'
                                     WHEN     hdr.duty_date IS NOT NULL
                                          AND hdr.in_dttm IS NULL
                                          AND HDR.OUT_DTTM IS NULL
                                     THEN
                                        'Absent'
                                  END
                                     day_status,
                                  'ACCESSORIES' reference
                             FROM hrm_employee@dblink_accs hed,
                                  gbl_dept@dblink_accs gd,
                                  gbl_company@dblink_accs gc,
                                  gbl_desig@dblink_accs gdg,
                                  (SELECT MAX(display_serial) sl,
                                          ref_pk_column_value employee_id
                                FROM gbl_attachments@dblink_accs
                                WHERE attachment_type_id = 1
                                GROUP BY ref_pk_column_value) att,
                                  (SELECT duty_date,
                                          in_dttm,
                                          out_dttm,
                                          employee_id
                                     FROM hrm_duty_roster@dblink_accs
                                    WHERE duty_date =  :p_date) hdr,
                                  (SELECT hla.employee_id, hla.application_dttm
                                     FROM hrm_leave_application@dblink_accs hla
                                    WHERE  :p_date BETWEEN TRUNC (hla.start_date)
                                                              AND TRUNC (hla.end_date)) leave
                            WHERE  hed.current_company_id = gc.company_id
                                  AND hed.current_dept_id = gd.dept_id
                                  AND hed.current_desig_id = gdg.desig_id
                                  AND hed.employee_id = hdr.employee_id
                                  AND hed.employee_id = att.employee_id(+)
                                  AND hed.employee_id = leave.employee_id(+)
                                  AND hed.employee_category_id = 4041
                                  AND hed.active_ind = 'Y'
                                  AND hed.current_company_id IN (1, 2, 5)
                                  AND (
                                       hed.auto_formated_id = :employee_id
                                       OR hed.auto_formated_id IN  (SELECT hea.emp_auto_id FROM hrm_employee_authority@dblink_accs hea WHERE hea.active_ind = 'Y' AND auth_emp_auto_id = :employee_id)
                                       --OR 'ACCESSORIES' = (SELECT soa.display_name FROM sec_objectaccess@dblink_accs soa  WHERE soa.object_id = 1001  AND soa.auto_formated_id = :employee_id AND soa.active_ind = 'Y')
                                       OR 'AppsAllData' = (SELECT display_name FROM sec_objectaccess WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                                           UNION ALL
                                                           SELECT display_name FROM sec_objectaccess@dblink_food WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                                           UNION ALL
                                                           SELECT display_name FROM sec_objectaccess@dblink_accs WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y')
                        --               OR hed.auto_formated_id IN (SELECT allow_employee_auto_id FROM employee_allows WHERE employee_auto_id = :employee_id
                        --                                           UNION ALL
                        --                                           SELECT allow_employee_auto_id FROM employee_allows@dblink_food WHERE employee_auto_id = :employee_id
                        --                                           UNION ALL
                        --                                           SELECT allow_employee_auto_id FROM employee_allows@dblink_accs WHERE employee_auto_id = :employee_id)
                                       ) 
                          )'''
        #print(l_employee_id)
        my_query = query_db(oracle_sql, {'employee_id': l_employee_id , 'p_date' : l_date})
        json_output = json.dumps(my_query)
        return HttpResponse(json_output)

def employee_job_card(request):
    if request.method == 'GET':
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_emp_id = l_dic["employee_id"]
        l_date = l_dic["p_date"]
        oracle_sql = '''SELECT employee_id,
                               joining_date,
                               desig_name,
                               work_mobile,
                               duration,
                               duty_date,
                               duty_date_full,
                               duty_day,
                               in_time,
                               out_time,
                               late_min,
                               late,
                               day_status
                        FROM       
                            (
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.work_mobile,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'DD-Mon-RRRR') duty_date_full,
                                       TO_CHAR(hdr.duty_date, 'Dy') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                             NULL
                                       END late,
                                       CASE
                                        WHEN get_employee_day_type (
                                               hed.company_id,
                                               hdr.duty_date,
                                               hed.employee_id) = 'Y'
                                       THEN
                                          CASE
                                             WHEN hrm_payroll.chk_half_day_leave (
                                                     hed.employee_id,
                                                     hdr.duty_date) = 'N'
                                             THEN
                                                CASE
                                                   WHEN hdr.in_dttm <=
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'P'
                                                   WHEN hdr.in_dttm >
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'L'
                                                   WHEN hdr.in_dttm IS NULL AND hdr.out_dttm IS NULL
                                                   THEN
                                                      CASE
                                                         WHEN get_leave_ind (
                                                                 hed.employee_id,
                                                                 hdr.duty_date) = 'Y'
                                                         THEN
                                                            hrm_payroll.get_leave_type (
                                                               hed.employee_id,
                                                               hdr.duty_date)
                                                         WHEN hdr.shift_id IS NULL
                                                         THEN
                                                            NULL
                                                         WHEN hdr.shift_id IS NOT NULL AND TRUNC(hdr.duty_date) <= TRUNC(SYSDATE) THEN
                                                            'A'
                                                      END
                                                END
                                             ELSE
                                                hrm_payroll.get_leave_type (
                                                   hed.employee_id,
                                                   hdr.duty_date)
                                          END
                                       ELSE
                                          CASE
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'W'
                                             THEN
                                                'PW'
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'H'
                                             THEN
                                                'PH'
                                             WHEN hdr.in_dttm IS NULL
                                             THEN
                                                get_employee_day_type (
                                                   hed.company_id,
                                                   hdr.duty_date,
                                                   hed.employee_id)
                                          END
                                       END day_status
                                FROM hrm_duty_roster hdr,
                                     hrm_employee_detail hed,
                                     hrm_shift hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(TO_DATE(:p_date), 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                                UNION ALL
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.work_mobile,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'DD-Mon-RRRR') duty_date_full,
                                       TO_CHAR(hdr.duty_date, 'Day') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff@dblink_food (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                             NULL
                                       END late,
                                       CASE
                                        WHEN get_employee_day_type@dblink_food (
                                               hed.company_id,
                                               hdr.duty_date,
                                               hed.employee_id) = 'Y'
                                       THEN
                                          CASE
                                             WHEN hrm_payroll.chk_half_day_leave (
                                                     hed.employee_id,
                                                     hdr.duty_date) = 'N'
                                             THEN
                                                CASE
                                                   WHEN hdr.in_dttm <=
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'P'
                                                   WHEN hdr.in_dttm >
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'L'
                                                   WHEN hdr.in_dttm IS NULL AND hdr.out_dttm IS NULL
                                                   THEN
                                                      CASE
                                                         WHEN get_leave_ind@dblink_food (
                                                                 hed.employee_id,
                                                                 hdr.duty_date) = 'Y'
                                                         THEN
                                                            hrm_payroll.get_leave_type@dblink_food (
                                                               hed.employee_id,
                                                               hdr.duty_date)
                                                         WHEN hdr.shift_id IS NULL
                                                         THEN
                                                            NULL
                                                         WHEN hdr.shift_id IS NOT NULL AND TRUNC(hdr.duty_date) <= TRUNC(SYSDATE) THEN 'A'
                                                      END
                                                END
                                             ELSE
                                                hrm_payroll.get_leave_type@dblink_food (
                                                   hed.employee_id,
                                                   hdr.duty_date)
                                          END
                                       ELSE
                                          CASE
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type@dblink_food (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'W'
                                             THEN
                                                'PW'
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type@dblink_food (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'H'
                                             THEN
                                                'PH'
                                             WHEN hdr.in_dttm IS NULL
                                             THEN
                                                get_employee_day_type@dblink_food (
                                                   hed.company_id,
                                                   hdr.duty_date,
                                                   hed.employee_id)
                                          END
                                       END day_status
                                FROM hrm_duty_roster@dblink_food hdr,
                                     hrm_employee_detail@dblink_food hed,
                                     hrm_shift@dblink_food hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(TO_DATE(:p_date), 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                                UNION ALL
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.work_mobile,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'DD-Mon-RRRR') duty_date_full,
                                       TO_CHAR(hdr.duty_date, 'Day') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff@dblink_accs (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                              NULL
                                       END late,
                                       CASE
                                        WHEN get_employee_day_type@dblink_accs (
                                               hed.company_id,
                                               hdr.duty_date,
                                               hed.employee_id) = 'Y'
                                       THEN
                                          CASE
                                             WHEN hrm_payroll.chk_half_day_leave (
                                                     hed.employee_id,
                                                     hdr.duty_date) = 'N'
                                             THEN
                                                CASE
                                                   WHEN hdr.in_dttm <=
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'P'
                                                   WHEN hdr.in_dttm >
                                                           TO_DATE (
                                                                 TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                              || LPAD (
                                                                      hs.shift_start_hour
                                                                    + FLOOR (
                                                                           (  hs.shift_start_minute
                                                                            + 16)
                                                                         / 60),
                                                                    2,
                                                                    '0')
                                                              || LPAD (
                                                                    MOD (
                                                                       (  hs.shift_start_minute
                                                                        + 16),
                                                                       60),
                                                                    2,
                                                                    '0'),
                                                              'ddmmrrhh24mi')
                                                   THEN
                                                      'L'
                                                   WHEN hdr.in_dttm IS NULL AND hdr.out_dttm IS NULL
                                                   THEN
                                                      CASE
                                                         WHEN get_leave_ind@dblink_accs (
                                                                 hed.employee_id,
                                                                 hdr.duty_date) = 'Y'
                                                         THEN
                                                            hrm_payroll.get_leave_type (
                                                               hed.employee_id,
                                                               hdr.duty_date)
                                                         WHEN hdr.shift_id IS NULL
                                                         THEN
                                                            NULL
                                                         WHEN hdr.shift_id IS NOT NULL AND TRUNC(hdr.duty_date) <= TRUNC(SYSDATE) THEN
                                                         'A'
                                                      END
                                                END
                                             ELSE
                                                hrm_payroll.get_leave_type@dblink_accs (
                                                   hed.employee_id,
                                                   hdr.duty_date)
                                          END
                                       ELSE
                                          CASE
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type@dblink_accs (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'W'
                                             THEN
                                                'PW'
                                             WHEN     hdr.in_dttm IS NOT NULL
                                                  AND get_employee_day_type@dblink_accs (
                                                         hed.company_id,
                                                         hdr.duty_date,
                                                         hed.employee_id) = 'H'
                                             THEN
                                                'PH'
                                             WHEN hdr.in_dttm IS NULL
                                             THEN
                                                get_employee_day_type@dblink_accs (
                                                   hed.company_id,
                                                   hdr.duty_date,
                                                   hed.employee_id)
                                          END
                                       END day_status
                                FROM hrm_duty_roster@dblink_accs hdr,
                                     hrm_employee_detail@dblink_accs hed,
                                     hrm_shift@dblink_accs hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(TO_DATE(:p_date), 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                            )
                        WHERE employee_id = :employee_id
                        ORDER BY duty_date'''
        my_query = query_db(oracle_sql, {'employee_id': l_emp_id, 'p_date': l_date} )
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

def leave_balance_info(request):
    if request.method == 'GET':
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        l_employee_id = l_dic["employee_id"]
        oracle_sql = '''SELECT m.leave_type_name,
                               hrm_payroll.get_leave_allocated_days(get_emp_id_from_afid(:employee_id), m.leave_type_id , TO_CHAR(SYSDATE, 'RRRR')) allocated,
                               hrm_payroll.get_leave_absorbed_days(get_emp_id_from_afid(:employee_id), m.leave_type_id , TO_CHAR(SYSDATE, 'RRRR')) + NVL(m.pipeline,0) consumed,
                               NVL(hrm_payroll.get_leave_allocated_days(get_emp_id_from_afid(:employee_id),m.leave_type_id,TO_CHAR(SYSDATE, 'RRRR')),0) - 
                               (NVL(hrm_payroll.get_leave_absorbed_days(get_emp_id_from_afid(:employee_id),m.leave_type_id,TO_CHAR(SYSDATE, 'RRRR')),0) + NVL(m.pipeline,0)) available
                        FROM hrm_employee he,
                             (
                                select hlt.leave_type_name,
                                       hlt.leave_type_id,
                                       hla.pipeline
                                from hrm_leave_type hlt,
                                     (
                                     SELECT la.leave_type_id,
                                            SUM(CASE WHEN lt.short_name <> 'STL' AND NVL(la.half_day_ind,'N') = 'Y' THEN  (NVL(la.application_for_days,0)/2) ELSE la.application_for_days END) pipeline
                                     FROM hrm_leave_application la,
                                          hrm_leave_type lt
                                     WHERE lt.leave_type_id = la.leave_type_id(+) 
                                     AND la.appr_by IS NULL
                                     AND la.auth_by IS NULL
                                     AND la.reco_by IS NULL
                                     AND la.status <> 'REJ'
                                     AND la.employee_id = get_emp_id_from_afid(:employee_id)
                                     AND EXTRACT(YEAR FROM la.start_date) = TO_CHAR(SYSDATE, 'RRRR') 
                                     GROUP BY la.leave_type_id
                                     ) hla
                                where hlt.leave_type_id = hla.leave_type_id(+) 
                                and hlt.company_id in (select current_company_id from hrm_employee where auto_formated_id = :employee_id)
                                and hlt.short_name in ('EL','CL', 'SL', 'STL')
                                order by hlt.leave_type_id
                             ) m
                        WHERE he.auto_formated_id = :employee_id 
                        UNION ALL
                        SELECT m.leave_type_name,
                               hrm_payroll.get_leave_allocated_days@dblink_food(get_emp_id_from_afid(:employee_id), m.leave_type_id , TO_CHAR(SYSDATE, 'RRRR')) allocated,
                               hrm_payroll.get_leave_absorbed_days@dblink_food(get_emp_id_from_afid(:employee_id), m.leave_type_id , TO_CHAR(SYSDATE, 'RRRR')) + NVL(m.pipeline,0) consumed,
                               NVL(hrm_payroll.get_leave_allocated_days@dblink_food(get_emp_id_from_afid(:employee_id),m.leave_type_id,TO_CHAR(SYSDATE, 'RRRR')),0) - 
                               (NVL(hrm_payroll.get_leave_absorbed_days@dblink_food(get_emp_id_from_afid(:employee_id),m.leave_type_id,TO_CHAR(SYSDATE, 'RRRR')),0) + NVL(m.pipeline,0)) available
                        FROM hrm_employee@dblink_food he,
                             (
                                select hlt.leave_type_name,
                                       hlt.leave_type_id,
                                       hla.pipeline
                                from hrm_leave_type@dblink_food hlt,
                                     (
                                     SELECT la.leave_type_id,
                                            SUM(CASE WHEN lt.short_name <> 'STL' AND NVL(la.half_day_ind,'N') = 'Y' THEN  (NVL(la.application_for_days,0)/2) ELSE la.application_for_days END) pipeline
                                     FROM hrm_leave_application@dblink_food la,
                                          hrm_leave_type@dblink_food lt
                                     WHERE lt.leave_type_id = la.leave_type_id(+) 
                                     AND la.appr_by IS NULL
                                     AND la.auth_by IS NULL
                                     AND la.reco_by IS NULL
                                     AND la.status <> 'REJ'
                                     AND la.employee_id = get_emp_id_from_afid(:employee_id)
                                     AND EXTRACT(YEAR FROM la.start_date) = TO_CHAR(SYSDATE, 'RRRR') 
                                     GROUP BY la.leave_type_id
                                     ) hla
                                where hlt.leave_type_id = hla.leave_type_id(+) 
                                and hlt.company_id in (select current_company_id from hrm_employee@dblink_food where auto_formated_id = :employee_id)
                                and hlt.short_name in ('EL','CL', 'SL', 'STL')
                                order by hlt.leave_type_id
                             ) m
                        WHERE he.auto_formated_id = :employee_id 
                        UNION ALL
                        SELECT m.leave_type_name,
                               hrm_payroll.get_leave_allocated_days@dblink_accs(get_emp_id_from_afid(:employee_id), m.leave_type_id , TO_CHAR(SYSDATE, 'RRRR')) allocated,
                               hrm_payroll.get_leave_absorbed_days@dblink_accs(get_emp_id_from_afid(:employee_id), m.leave_type_id , TO_CHAR(SYSDATE, 'RRRR')) + NVL(m.pipeline,0) consumed,
                               NVL(hrm_payroll.get_leave_allocated_days@dblink_accs(get_emp_id_from_afid(:employee_id),m.leave_type_id,TO_CHAR(SYSDATE, 'RRRR')),0) - 
                               (NVL(hrm_payroll.get_leave_absorbed_days@dblink_accs(get_emp_id_from_afid(:employee_id),m.leave_type_id,TO_CHAR(SYSDATE, 'RRRR')),0) + NVL(m.pipeline,0)) available
                        FROM hrm_employee@dblink_accs he,
                             (
                                select hlt.leave_type_name,
                                       hlt.leave_type_id,
                                       hla.pipeline
                                from hrm_leave_type@dblink_accs hlt,
                                     (
                                     SELECT la.leave_type_id,
                                            SUM(CASE WHEN lt.short_name <> 'STL' AND NVL(la.half_day_ind,'N') = 'Y' THEN  (NVL(la.application_for_days,0)/2) ELSE la.application_for_days END) pipeline
                                     FROM hrm_leave_application@dblink_accs la,
                                          hrm_leave_type@dblink_accs lt
                                     WHERE lt.leave_type_id = la.leave_type_id(+) 
                                     AND la.appr_by IS NULL
                                     AND la.auth_by IS NULL
                                     AND la.reco_by IS NULL
                                     AND la.status <> 'REJ'
                                     AND la.employee_id = get_emp_id_from_afid(:employee_id)
                                     AND EXTRACT(YEAR FROM la.start_date) = TO_CHAR(SYSDATE, 'RRRR') 
                                     GROUP BY la.leave_type_id
                                     ) hla
                                where hlt.leave_type_id = hla.leave_type_id(+) 
                                and hlt.company_id in (select current_company_id from hrm_employee@dblink_accs where auto_formated_id = :employee_id)
                                and hlt.short_name in ('EL','CL', 'SL', 'STL')
                                order by hlt.leave_type_id
                             ) m
                        WHERE he.auto_formated_id = :employee_id 
                        ORDER BY 1'''
        my_query = query_db(oracle_sql , {'employee_id': l_employee_id})
        json_output = json.dumps(my_query)
        return HttpResponse(json_output)

def late_attendance_list(request):
    if request.method == 'GET':
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        l_month_year = l_dic["month_year"]
        l_employee_id = l_dic["employee_id"]
        oracle_sql = '''SELECT DENSE_RANK() OVER(PARTITION BY dept_name ORDER BY dept_name, display_serial, employee_full_name) sl,
                           employee_full_name,
                           desig_name,
                           auto_formated_id,
                           employee_id,
                           dept_name,
                           company sbu,
                           display_serial,
                           late_count,
                           reference,
                           image_url
                        FROM 
                        (   SELECT DISTINCT hed.employee_full_name,
                               hed.desig_name,
                               hed.auto_formated_id,
                               hed.employee_id,
                               hed.dept_name,
                               hed.company,
                               hed.display_serial,
                               SUM(
                                     CASE
                                         WHEN hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| 16,'ddmmrrhh24mi') THEN 
                                              1 
                                         ELSE 0 
                                     END
                                 ) OVER(PARTITION BY hed.employee_id) late_count,
                               'GROUP' reference,
                               'http://103.199.108.43/GROUP/EMPLOYEEPHOTO'
                                || hed.employee_id
                                || NVL (
                                      att.sl,
                                      1)
                                || '.JPG' image_url
                        FROM hrm_employee_detail hed,
                             (SELECT *
                             FROM hrm_duty_roster hdr
                             WHERE TO_CHAR(hdr.duty_date,'MMRRRR') = TO_CHAR(TO_DATE(:p_month_year),'MMRRRR')
                             AND hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| '16','ddmmrrhh24mi')) hdr,
                             (SELECT MAX(display_serial) sl,
                                      ref_pk_column_value employee_id
                            FROM gbl_attachments
                            WHERE attachment_type_id = 1
                            GROUP BY ref_pk_column_value) att
                        WHERE hed.employee_id = hdr.employee_id(+)
                        AND hed.employee_id = att.employee_id(+)
                        AND hed.employment_end_date IS NULL
                        AND hed.employee_category_id = 4041
                        AND hed.company_id IN (1,13)
                        AND hed.active_ind = 'Y'
                        AND (
                           hed.auto_formated_id = :employee_id
                           OR hed.auto_formated_id IN  (SELECT hea.emp_auto_id FROM hrm_employee_authority hea WHERE hea.active_ind = 'Y' AND auth_emp_auto_id = :employee_id)
                        --OR 'GROUP' = (SELECT soa.display_name FROM sec_objectaccess soa  WHERE soa.object_id = 1001  AND soa.auto_formated_id = :employee_id AND soa.active_ind = 'Y')
                           OR 'AppsAllData' = (SELECT display_name FROM sec_objectaccess WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                               UNION ALL
                                               SELECT display_name FROM sec_objectaccess@dblink_food WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                               UNION ALL
                                               SELECT display_name FROM sec_objectaccess@dblink_accs WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y')
                        --OR hed.auto_formated_id IN (SELECT allow_employee_auto_id FROM employee_allows WHERE employee_auto_id = :employee_id
                        --                            UNION ALL
                        --                            SELECT allow_employee_auto_id FROM employee_allows@dblink_food WHERE employee_auto_id = :employee_id
                        --                            UNION ALL
                        --                            SELECT allow_employee_auto_id FROM employee_allows@dblink_accs WHERE employee_auto_id = :employee_id)
                           ) 
                        UNION ALL
                        SELECT DISTINCT hed.employee_full_name,
                               hed.desig_name,
                               hed.auto_formated_id,
                               hed.employee_id,
                               hed.dept_name,
                               hed.company,
                               hed.display_serial,
                               SUM(
                                     CASE
                                         WHEN hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| 16,'ddmmrrhh24mi') THEN 
                                              1 
                                         ELSE 0 
                                     END
                                 ) OVER(PARTITION BY hed.employee_id) late_count,
                               'FOOD' reference,
                               'http://103.199.108.43/FOOD/EMPLOYEEPHOTO'
                                || hed.employee_id
                                || NVL (
                                      att.sl,
                                      1)
                                || '.JPG' image_url
                        FROM hrm_employee_detail@dblink_food hed,
                             (SELECT duty_date,
                                     in_dttm,
                                     out_dttm,
                                     employee_id
                             FROM hrm_duty_roster@dblink_food hdr
                             WHERE TO_CHAR(hdr.duty_date,'MMRRRR') = TO_CHAR(TO_DATE(:p_month_year),'MMRRRR') 
                             AND hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| '16','ddmmrrhh24mi')) hdr,
                             (SELECT MAX(display_serial) sl,
                                      ref_pk_column_value employee_id
                            FROM gbl_attachments@dblink_food
                            WHERE attachment_type_id = 1
                            GROUP BY ref_pk_column_value) att
                        WHERE hed.employee_id = hdr.employee_id(+)
                        AND hed.employee_id = att.employee_id(+)
                        AND hed.employment_end_date IS NULL
                        AND hed.employee_category_id = 4041
                        AND hed.company_id = 1
                        AND hed.active_ind = 'Y'
                        AND (
                           hed.auto_formated_id = :employee_id
                           OR hed.auto_formated_id IN  (SELECT hea.emp_auto_id FROM hrm_employee_authority@dblink_food hea WHERE hea.active_ind = 'Y' AND auth_emp_auto_id = :employee_id)
                        --OR 'FOOD' = (SELECT soa.display_name FROM sec_objectaccess soa  WHERE soa.object_id = 1001  AND soa.auto_formated_id = :employee_id AND soa.active_ind = 'Y')
                           OR 'AppsAllData' = (SELECT display_name FROM sec_objectaccess WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                               UNION ALL
                                               SELECT display_name FROM sec_objectaccess@dblink_food WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                               UNION ALL
                                               SELECT display_name FROM sec_objectaccess@dblink_accs WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y')
                        --OR hed.auto_formated_id IN (SELECT allow_employee_auto_id FROM employee_allows WHERE employee_auto_id = :employee_id
                        --                            UNION ALL
                        --                            SELECT allow_employee_auto_id FROM employee_allows@dblink_food WHERE employee_auto_id = :employee_id
                        --                            UNION ALL
                        --                            SELECT allow_employee_auto_id FROM employee_allows@dblink_accs WHERE employee_auto_id = :employee_id)
                           ) 
                        UNION ALL
                        SELECT DISTINCT hed.employee_full_name,
                               hed.desig_name,
                               hed.auto_formated_id,
                               hed.employee_id,
                               hed.dept_name,
                               hed.company,
                               hed.display_serial,
                               SUM(
                                     CASE
                                         WHEN hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| 16,'ddmmrrhh24mi') THEN 
                                              1 
                                         ELSE 0 
                                     END
                                 ) OVER(PARTITION BY hed.employee_id) late_count,
                               'ACCESSORIES' reference,
                               'http://103.199.108.43/ACCESSORIES/EMPLOYEEPHOTO'
                                || hed.employee_id
                                || NVL (
                                      att.sl,
                                      1)
                                || '.JPG' image_url
                        FROM hrm_employee_detail@dblink_accs hed,
                             (SELECT *
                             FROM hrm_duty_roster@dblink_accs hdr
                             WHERE TO_CHAR(hdr.duty_date,'MMRRRR') = TO_CHAR(TO_DATE(:p_month_year),'MMRRRR') 
                             AND hdr.in_dttm >  TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| '09'|| '16','ddmmrrhh24mi')) hdr,
                             (SELECT MAX(display_serial) sl,
                                      ref_pk_column_value employee_id
                            FROM gbl_attachments@dblink_accs
                            WHERE attachment_type_id = 1
                            GROUP BY ref_pk_column_value) att
                        WHERE hed.employee_id = hdr.employee_id(+)
                        AND hed.employee_id = att.employee_id(+)
                        AND hed.employment_end_date IS NULL
                        AND hed.employee_category_id = 4041
                        AND hed.company_id IN (1, 2, 5)
                        AND hed.active_ind = 'Y'
                        AND (
                           hed.auto_formated_id = :employee_id
                           OR hed.auto_formated_id IN  (SELECT hea.emp_auto_id FROM hrm_employee_authority@dblink_accs hea WHERE hea.active_ind = 'Y' AND auth_emp_auto_id = :employee_id)
                        --OR 'FOOD' = (SELECT soa.display_name FROM sec_objectaccess soa  WHERE soa.object_id = 1001  AND soa.auto_formated_id = :employee_id AND soa.active_ind = 'Y')
                           OR 'AppsAllData' = (SELECT display_name FROM sec_objectaccess WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                               UNION ALL
                                               SELECT display_name FROM sec_objectaccess@dblink_food WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y'
                                               UNION ALL
                                               SELECT display_name FROM sec_objectaccess@dblink_accs WHERE object_id = 1000 AND auto_formated_id = :employee_id AND active_ind = 'Y')
                        --OR hed.auto_formated_id IN (SELECT allow_employee_auto_id FROM employee_allows WHERE employee_auto_id = :employee_id
                        --                            UNION ALL
                        --                            SELECT allow_employee_auto_id FROM employee_allows@dblink_food WHERE employee_auto_id = :employee_id
                        --                            UNION ALL
                        --                            SELECT allow_employee_auto_id FROM employee_allows@dblink_accs WHERE employee_auto_id = :employee_id)
                           )  
                        ) 
                        WHERE late_count >= 6
                        ORDER BY late_count DESC'''
        my_query = query_db(oracle_sql,{'p_month_year':l_month_year,'employee_id' : l_employee_id})
        json_output = json.dumps(my_query)
        return HttpResponse(json_output)

def day_status(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        l_employee_id = l_dic["employee_id"]
        oracle_sql = '''SELECT CASE
                                     WHEN hdr.in_dttm IS NOT NULL OR hdr.out_dttm IS NOT NULL
                                     THEN
                                        CASE
                                           WHEN hdr.in_dttm >=
                                                   TO_DATE (
                                                         TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                      ||'09'||'1600',
                                                      'ddmmrrhh24miss')
                                           THEN
                                              'Present-Late'
                                           ELSE
                                              'Present-OnTime'
                                        END
                                     WHEN     hdr.in_dttm IS NULL
                                          AND hdr.out_dttm IS NULL
                                          AND leave.application_dttm IS NOT NULL
                                     THEN
                                        'Leave'
                                     WHEN     hdr.duty_date IS NOT NULL
                                          AND hdr.in_dttm IS NULL
                                          AND hdr.out_dttm IS NULL
                                     THEN
                                        'Absent'
                                  END day_status
                                FROM hrm_duty_roster hdr,
                                     (SELECT hla.employee_id, hla.application_dttm
                                      FROM hrm_leave_application hla
                                      WHERE SYSDATE BETWEEN TRUNC (hla.start_date)
                                                              AND TRUNC (hla.end_date)) leave
                                WHERE hdr.employee_id = leave.employee_id(+)
                                AND duty_date = TRUNC(SYSDATE)
                                AND get_emp_office_id(hdr.employee_id) = :employee_id
                                UNION ALL
                                SELECT CASE
                                     WHEN hdr.in_dttm IS NOT NULL OR hdr.out_dttm IS NOT NULL
                                     THEN
                                        CASE
                                           WHEN hdr.in_dttm >=
                                                   TO_DATE (
                                                         TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                      ||'09'||'1600',
                                                      'ddmmrrhh24miss')
                                           THEN
                                              'Present-Late'
                                           ELSE
                                              'Present-OnTime'
                                        END
                                     WHEN     hdr.in_dttm IS NULL
                                          AND hdr.out_dttm IS NULL
                                          AND leave.application_dttm IS NOT NULL
                                     THEN
                                        'Leave'
                                     WHEN     hdr.duty_date IS NOT NULL
                                          AND hdr.in_dttm IS NULL
                                          AND hdr.out_dttm IS NULL
                                     THEN
                                        'Absent'
                                  END day_status
                                FROM hrm_duty_roster@dblink_food hdr,
                                     (SELECT hla.employee_id, hla.application_dttm
                                      FROM hrm_leave_application@dblink_food hla
                                      WHERE SYSDATE BETWEEN TRUNC (hla.start_date)
                                                              AND TRUNC (hla.end_date)) leave
                                WHERE hdr.employee_id = leave.employee_id(+)
                                AND duty_date = TRUNC(SYSDATE)
                                AND get_emp_office_id@dblink_food(hdr.employee_id) = :employee_id
                                UNION ALL
                                SELECT CASE
                                     WHEN hdr.in_dttm IS NOT NULL OR hdr.out_dttm IS NOT NULL
                                     THEN
                                        CASE
                                           WHEN hdr.in_dttm >=
                                                   TO_DATE (
                                                         TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                      ||'09'||'1600',
                                                      'ddmmrrhh24miss')
                                           THEN
                                              'Present-Late'
                                           ELSE
                                              'Present-OnTime'
                                        END
                                     WHEN     hdr.in_dttm IS NULL
                                          AND hdr.out_dttm IS NULL
                                          AND leave.application_dttm IS NOT NULL
                                     THEN
                                        'Leave'
                                     WHEN     hdr.duty_date IS NOT NULL
                                          AND hdr.in_dttm IS NULL
                                          AND hdr.out_dttm IS NULL
                                     THEN
                                        'Absent'
                                  END day_status
                                FROM hrm_duty_roster@dblink_accs hdr,
                                     (SELECT hla.employee_id, hla.application_dttm
                                      FROM hrm_leave_application@dblink_accs hla
                                      WHERE SYSDATE BETWEEN TRUNC (hla.start_date)
                                                              AND TRUNC (hla.end_date)) leave
                                WHERE hdr.employee_id = leave.employee_id(+)
                                AND duty_date = TRUNC(SYSDATE)
                                AND get_emp_office_id@dblink_accs(hdr.employee_id) = :employee_id'''
        my_query = query_db(oracle_sql, {'employee_id': l_employee_id})
        json_output = json.dumps(my_query)
        return HttpResponse(False)

def responsibility_handover_to(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        l_employee_id = l_dic["employee_id"]
        oracle_sql = '''SELECT he.employee_id,
                               he.auto_formated_id,
                               he.manually_formatted_id,
                               REGEXP_REPLACE(
                                    TRIM(
                                        he.first_name || ' '
                                        ||
                                        he.middle_name || ' '
                                        ||
                                        he.last_name
                                    ),
                                    '[[:space:]]+',
                                    ' '
                                ) employee_name,
                               he.work_mobile, 
                               gdg.desig_name,
                               gdp.dept_name,
                               gdv.division_name,
                               gc.short_name unit_short_name
                        FROM hrm_employee he,
                             hrm_employee he_user,
                             gbl_desig gdg,
                             gbl_dept gdp,
                             gbl_division gdv,
                             gbl_company gc,
                             user_units uu,
                             hrm_employee_category ec
                        WHERE he.current_desig_id = gdg.desig_id(+)
                        AND he.current_dept_id = gdp.dept_id(+)
                        AND he.current_division_id = gdv.division_id(+)
                        AND he.current_company_id = gc.company_id
                        AND he.current_company_id = uu.unit_dept_no
                        AND he.employee_category_id = ec.employee_category_id
                        AND ec.filtered_ind <> 'Y' 
                        AND get_emp_office_id(uu.user_id) = :employee_id
                        AND he.active_ind = 'Y'
                        AND get_emp_office_id(he_user.employee_id) = :employee_id
                        AND (
                            NVL(he.current_division_id, he.joining_division_id) = NVL(he_user.current_division_id, he_user.joining_division_id)
                            OR NVL(he.current_dept_id, he.joining_dept_id) = NVL(he_user.current_dept_id, he_user.joining_dept_id)
                        )
                        UNION ALL
                        SELECT he.employee_id,
                               he.auto_formated_id,
                               he.manually_formatted_id,
                               REGEXP_REPLACE(
                                    TRIM(
                                        he.first_name || ' '
                                        ||
                                        he.middle_name || ' '
                                        ||
                                        he.last_name
                                    ),
                                    '[[:space:]]+',
                                    ' '
                                ) employee_name,
                               he.work_mobile, 
                               gdg.desig_name,
                               gdp.dept_name,
                               gdv.division_name,
                               gc.short_name unit_short_name
                        FROM hrm_employee@dblink_food he,
                             hrm_employee@dblink_food he_user,
                             gbl_desig@dblink_food gdg,
                             gbl_dept@dblink_food gdp,
                             gbl_division@dblink_food gdv,
                             gbl_company@dblink_food gc,
                             user_units@dblink_food uu,
                             hrm_employee_category@dblink_food ec
                        WHERE he.current_desig_id = gdg.desig_id(+)
                        AND he.current_dept_id = gdp.dept_id(+)
                        AND he.current_division_id = gdv.division_id(+)
                        AND he.current_company_id = gc.company_id
                        AND he.current_company_id = uu.unit_dept_no
                        AND he.employee_category_id = ec.employee_category_id
                        AND ec.filtered_ind <> 'Y' 
                        AND get_emp_office_id@dblink_food(uu.user_id) = :employee_id
                        AND he.active_ind = 'Y'
                        AND get_emp_office_id@dblink_food(he_user.employee_id) = :employee_id
                        AND (
                            NVL(he.current_division_id, he.joining_division_id) = NVL(he_user.current_division_id, he_user.joining_division_id)
                            OR NVL(he.current_dept_id, he.joining_dept_id) = NVL(he_user.current_dept_id, he_user.joining_dept_id)
                        )
                        UNION ALL
                        SELECT he.employee_id,
                               he.auto_formated_id,
                               he.manually_formatted_id,
                               REGEXP_REPLACE(
                                    TRIM(
                                        he.first_name || ' '
                                        ||
                                        he.middle_name || ' '
                                        ||
                                        he.last_name
                                    ),
                                    '[[:space:]]+',
                                    ' '
                                ) employee_name,
                               he.work_mobile, 
                               gdg.desig_name,
                               gdp.dept_name,
                               gdv.division_name,
                               gc.short_name unit_short_name
                        FROM hrm_employee@dblink_accs he,
                             hrm_employee@dblink_accs he_user,
                             gbl_desig@dblink_accs gdg,
                             gbl_dept@dblink_accs gdp,
                             gbl_division@dblink_accs gdv,
                             gbl_company@dblink_accs gc,
                             user_units@dblink_accs uu,
                             hrm_employee_category@dblink_accs ec
                        WHERE he.current_desig_id = gdg.desig_id(+)
                        AND he.current_dept_id = gdp.dept_id(+)
                        AND he.current_division_id = gdv.division_id(+)
                        AND he.current_company_id = gc.company_id
                        AND he.current_company_id = uu.unit_dept_no
                        AND he.employee_category_id = ec.employee_category_id
                        AND ec.filtered_ind <> 'Y' 
                        AND get_emp_office_id@dblink_accs(uu.user_id) = :employee_id
                        AND he.active_ind = 'Y'
                        AND get_emp_office_id@dblink_accs(he_user.employee_id) = :employee_id
                        AND (
                            NVL(he.current_division_id, he.joining_division_id) = NVL(he_user.current_division_id, he_user.joining_division_id)
                            OR NVL(he.current_dept_id, he.joining_dept_id) = NVL(he_user.current_dept_id, he_user.joining_dept_id)
                        )    '''
        my_query = query_db(oracle_sql, {'employee_id': l_employee_id})
        json_output = json.dumps(my_query)
        return HttpResponse(json_output)

def office_calendar(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        l_employee_id = l_dic["employee_id"]
        l_date = l_dic["p_date"]
        oracle_sql = '''SELECT dt, note
                        FROM 
                        (SELECT dt dt1, TO_CHAR(dt, 'DD-MM-RRRR') dt, note
                        FROM prod_days
                        WHERE SUBSTR(pid, 7) = (SELECT company_id FROM hrm_employee_detail WHERE auto_formated_id = :p_employee_id)
                        AND day_type > 1
                        AND TO_CHAR(dt, 'RRRR') = TO_CHAR(TO_DATE(:p_date), 'RRRR')
                        UNION ALL
                        SELECT dt dt1,  TO_CHAR(dt, 'DD-MM-RRRR') dt, note
                        FROM prod_days@dblink_food pd
                        WHERE SUBSTR(pid, 7) = (SELECT company_id FROM hrm_employee_detail@dblink_food WHERE auto_formated_id = :p_employee_id)
                        AND TO_CHAR(dt, 'RRRR') = TO_CHAR(TO_DATE(:p_date), 'RRRR')
                        AND day_type > 1
                        UNION ALL
                        SELECT dt dt1, TO_CHAR(dt, 'DD-MM-RRRR') dt, note
                        FROM prod_days@dblink_food pd
                        WHERE SUBSTR(pid, 7) = (SELECT company_id FROM hrm_employee_detail@dblink_food WHERE auto_formated_id = :p_employee_id)
                        AND TO_CHAR(dt, 'RRRR') = TO_CHAR(TO_DATE(:p_date), 'RRRR')
                        AND day_type > 1
                        ORDER BY 1)'''
        my_query = query_db(oracle_sql, {'p_employee_id': l_employee_id , 'p_date':l_date})
        json_output = json.dumps(my_query)
        return HttpResponse(False)

def monthly_canteen_menu(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        l_employee_id = l_dic["employee_id"]
        l_date = l_dic["p_date"]
        oracle_sql = '''SELECT TO_CHAR(ctd.lunch_date,'DD-MM-RRRR') lunch_date,
                               ctd.lunch_type,
                               cm.item1 main_item,
                               cm.item2,
                               cm.item3,
                               cm.item4,
                               cm.item5,
                               NVL(ctd.meal_eaten, 0) meal_eaten,
                               TO_CHAR(ctd.no_of_token) is_active
                        FROM can_token ct,
                             can_token_detail ctd,
                             hrm_employee_detail hed,
                             can_menu cm
                        WHERE ct.id = ctd.master_id(+)
                        AND hed.employee_id = ct.employee_id(+)
                        AND ctd.lunch_date = cm.token_date(+)
                        AND TO_CHAR(ctd.lunch_date, 'MONRRRR') = TO_CHAR(TO_DATE(:p_date),'MONRRRR')
                        AND hed.auto_formated_id = :employee_id
                        AND ct.reference_name = 'GROUP'
                        UNION ALL
                        SELECT TO_CHAR(ctd.lunch_date,'DD-MM-RRRR') lunch_date,
                               ctd.lunch_type,
                               cm.item1 main_item,
                               cm.item2,
                               cm.item3,
                               cm.item4,
                               cm.item5,
                               NVL(ctd.meal_eaten, 0) meal_eaten,
                               TO_CHAR(ctd.no_of_token) is_active
                        FROM can_token ct,
                             can_token_detail ctd,
                             hrm_employee_detail@dblink_food hed,
                             can_menu cm
                        WHERE ct.id = ctd.master_id(+)
                        AND hed.employee_id = ct.employee_id(+)
                        AND TO_CHAR(ctd.lunch_date, 'MONRRRR') = TO_CHAR(TO_DATE(:p_date),'MONRRRR')
                        AND hed.auto_formated_id = :employee_id
                        AND ct.reference_name = 'FOOD'
                        UNION ALL
                        SELECT TO_CHAR(ctd.lunch_date,'DD-MM-RRRR') lunch_date,
                               ctd.lunch_type,
                               cm.item1 main_item,
                               cm.item2,
                               cm.item3,
                               cm.item4,
                               cm.item5,
                               NVL(ctd.meal_eaten, 0) meal_eaten,
                               TO_CHAR(ctd.no_of_token) is_active
                        FROM can_token ct,
                             can_token_detail ctd,
                             hrm_employee_detail@dblink_accs hed,
                             can_menu cm
                        WHERE ct.id = ctd.master_id(+)
                        AND hed.employee_id = ct.employee_id(+)
                        AND TO_CHAR(ctd.lunch_date, 'MONRRRR') = TO_CHAR(TO_DATE(:p_date),'MONRRRR')
                        AND hed.auto_formated_id = :employee_id
                        AND ct.reference_name IN ('ACCESSORIES','DLLL')'''
        my_query = query_db(oracle_sql, {'employee_id': l_employee_id , 'p_date':l_date})
        json_output = json.dumps(my_query)
        return HttpResponse(json_output)

def leave_days(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        l_employee_id = l_dic["employee_id"]
        l_start_date = l_dic["p_start_date"]
        l_end_date = l_dic["p_end_date"]
        oracle_sql = '''SELECT SUM(A) leave_days
                        FROM (
                            SELECT COUNT(*) A
                            FROM prod_days
                            WHERE SUBSTR(pid, 7) = (SELECT current_company_id FROM hrm_employee WHERE auto_formated_id = :employee_id)
                            AND dt BETWEEN :p_start_date AND :p_end_date
                            AND day_type = 0
                            UNION ALL
                            SELECT COUNT(*) A
                            FROM prod_days@dblink_food
                            WHERE SUBSTR(pid, 7) = (SELECT current_company_id FROM hrm_employee@dblink_food WHERE auto_formated_id = :employee_id)
                            AND dt BETWEEN :p_start_date AND :p_end_date
                            AND day_type = 0
                            UNION ALL
                            SELECT COUNT(*) A
                            FROM prod_days@dblink_accs
                            WHERE SUBSTR(pid, 7) = (SELECT current_company_id FROM hrm_employee@dblink_accs WHERE auto_formated_id = :employee_id)
                            AND dt BETWEEN :p_start_date AND :p_end_date
                            AND day_type = 0)'''
        my_query = query_db(oracle_sql, {'employee_id': l_employee_id , 'p_start_date':l_start_date, 'p_end_date':l_end_date})
        json_output = json.dumps(my_query)
        return HttpResponse(json_output)

def token_cancel_request(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_employee_id = l_dic["employee_id"]
        l_lunch_date = l_dic["lunch_date"]
        cur_oracle.callproc("front_end_support_tool.token_cancel_request", [l_employee_id,l_lunch_date])
        con.commit()
        return HttpResponse(True)

def leave_application(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_group()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        #print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_employee_id = l_dic["employee_id"]
        l_leave_type = l_dic["leave_type"]
        l_start_date = l_dic["start_date"]
        l_end_date = l_dic["end_date"]
        l_purpose = l_dic["purpose"]
        l_note = l_dic["note"]
        l_res_handover = l_dic["res_handover"]
        l_out_message = cur_oracle.var(str)
        '''
        cur_oracle.callproc("front_end_support_tool.ins_leave_application",
                            [l_employee_id,
                             l_leave_type,
                             l_start_date,
                             l_end_date,
                             l_purpose,
                             l_note,
                             l_res_handover,
                             l_out_message])'''
        con.commit()
        l_out = l_out_message.getvalue()
        l_out_json = {"error_message": l_out}
        if l_out is None:
            return HttpResponse(True)
        else:
            return HttpResponse(json.dumps(l_out_json))