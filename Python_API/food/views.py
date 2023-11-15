# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse

# Create your views here.

from django.views import View
import cx_Oracle
import json
import datetime
import ast

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
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        print(db_connection_info)
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

###############################################################################    user credential , previlege

def user_authentication_food(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_user_name = l_dic["user_name"]
        l_pass_word = l_dic["pass_word"]
        l_result = cur_oracle.callfunc('front_end_support_tool.check_login_credential_food', cx_Oracle.NUMBER,
                                       (l_user_name, l_pass_word))
        l_emp_id = cur_oracle.callfunc('front_end_support_tool.get_emp_id_food', cx_Oracle.NUMBER,
                                       (l_user_name, l_pass_word))
        l_employee_office_id = cur_oracle.callfunc('front_end_support_tool.get_employee_office_id_food', cx_Oracle.STRING,
                                                   (l_user_name, l_pass_word))

        l_spo_name = cur_oracle.callfunc('front_end_support_tool.get_spo_name',
                                                   cx_Oracle.STRING,
                                                   (l_user_name, l_pass_word))

        l_territory = cur_oracle.callfunc('front_end_support_tool.get_spo_territory', cx_Oracle.STRING,
                                                   [l_employee_office_id])
        l_area = cur_oracle.callfunc('front_end_support_tool.get_spo_area', cx_Oracle.STRING,
                                                   [l_employee_office_id])
        l_asm = cur_oracle.callfunc('front_end_support_tool.get_spo_asm', cx_Oracle.STRING,
                                                   [l_employee_office_id])
        con.commit()
        l_authentication_result = {"authentication_result": l_result, "employee_office_id": l_employee_office_id,
                                   "employee_ref_id": int(l_emp_id), 'spo_name' : l_spo_name ,"territory": l_territory, "area" : l_area, "asm": l_asm}
        l_json_output_1 = json.dumps(l_authentication_result)
        return HttpResponse(False)

def user_priv_food(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_emp_id = l_dic["employee_ref_id"]
        oracle_sql = '''WITH order_last_visit AS (
                            SELECT MAX(oom.order_date) outlet_last_visit,
                                   oom.outlet_id
                            FROM outlet_order_mst oom
                            GROUP BY oom.outlet_id
                        )
                        SELECT shop_full_name outlet,
                               smr.route_name,
                               su.store_unit_name distributor,
                               oi.proprietor_name,
                               oi.mobile_no1,
                               oi.latitude,
                               oi.longitude,
                               order_last_visit.outlet_last_visit,
                               '103.199.108.43\OUTLET_IMAGES\'||oi.shop_image_path image_url,
                               oi.id outlet_id,
                               oi.route_id,
                               oi.distributor_id
                        FROM sales_spo_tso_route sstr,
                             sales_market_route smr,
                             outlet_info oi,
                             order_last_visit,
                             store_unit su
                        WHERE sstr.route_id = smr.id(+)
                        AND smr.id = oi.route_id(+)
                        AND oi.id = order_last_visit.outlet_id(+)
                        AND oi.distributor_id = su.pid(+)
                        AND sstr.spo_tso_id = :p_spo_id'''
        my_query = query_db(oracle_sql, {'p_spo_id': l_emp_id})
        l_json_output = json.dumps(my_query, default=myconverter)
        return HttpResponse(l_json_output)

################################################################################  info for spo

def info_for_spo(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        l_spo_id = l_dic["spo_id"]
        l_date = l_dic["data_of_date"]
        l_target = cur_oracle.callfunc('front_end_support_tool.get_spo_target',
                                                   cx_Oracle.NUMBER,
                                                   (l_spo_id, l_date))
        l_achievement = cur_oracle.callfunc('front_end_support_tool.get_spo_achievement',
                                       cx_Oracle.NUMBER,
                                       (l_spo_id, l_date))

        l_sms_count = cur_oracle.callfunc('front_end_support_tool.get_ims_count',
                                            cx_Oracle.NUMBER,
                                            (l_spo_id, l_date))

        l_today_formatted_sms = cur_oracle.callfunc('front_end_support_tool.get_today_formatted_sms',
                                          cx_Oracle.STRING,
                                          [l_spo_id])

        l_result = {"target": l_target, "achievement": l_achievement,
                                   "formatted_sms_count": l_sms_count, "today_formatted_sms": l_today_formatted_sms}
        l_json_output = json.dumps(l_result)
        return HttpResponse(l_json_output)


################################################################################   query products, unit, trade offer

def food_category_product(request):
    if request.method == 'GET':
        oracle_sql = '''WITH t_offer
                        AS (
                        SELECT  t.item_pid trade_item_id,
                                t.trade_qty,
                                iu.short_name trade_unit,
                                t.offer_item offer_item_id,
                                oi.item_name offer_item_name,
                                t.offer_qty,
                                ou.short_name offer_unit
                        FROM trade_offer t,
                             item ai,
                             item oi,
                             unit iu,
                             unit ou
                        WHERE t.item_pid = ai.pid(+)
                        AND t.offer_item = oi.pid(+)
                        AND ai.market_unit_pid = iu.pid(+) 
                        AND t.unit_pid = ou.pid(+)
                        AND SYSDATE BETWEEN t.offer_from AND NVL(t.emergency_end_date,t.offer_to)
                        )
                        SELECT  ig.group_name item_category,
                                i.item_name,
                                i.item_code,
                                i.tp unit_price,
                                u.short_name unit_name,
                                mu.short_name market_unit,
                                i.conversion_value,
                                'http://103.199.108.43/FOOD_PRODUCTS/'||i.pid||'.jpg' image_url,
                                i.pid item_id,
                                TO_CHAR(NVL(t_offer.trade_qty,0)) trade_qty,
                                t_offer.offer_item_id,
                                t_offer.offer_item_name,
                                t_offer.offer_qty,
                                t_offer.offer_unit
                        FROM item_group ig,
                             item i,
                             unit u,
                             unit mu,
                             t_offer
                        WHERE ig.pid = i.item_group_pid(+)
                        AND i.unit_pid = u.pid(+)
                        AND i.market_unit_pid = mu.pid(+)
                        AND i.pid = t_offer.trade_item_id(+)
                        AND i.active_status = 'Y'
                        AND ig.is_active = 1
                        ORDER BY 1,2'''
        my_query = query_db(oracle_sql)
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

def query_units(request):
    if request.method == 'GET':
        oracle_sql = '''SELECT pid unit_id,
                        short_name unit_name
                        FROM unit'''
        my_query = query_db(oracle_sql)
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

def trade_offer(request):
    if request.method == 'GET':
        oracle_sql = '''SELECT t.item_pid trade_item_id,
                               t.trade_qty,
                               iu.short_name trade_unit,
                               t.offer_item offer_item_id,
                               oi.item_name offer_item_name,
                               t.offer_qty,
                               ou.short_name offer_unit
                        FROM trade_offer t,
                             item ai,
                             item oi,
                             unit iu,
                             unit ou
                        WHERE t.item_pid = ai.pid(+)
                        AND t.offer_item = oi.pid(+)
                        AND ai.market_unit_pid = iu.pid(+)
                        AND t.unit_pid = ou.pid(+)
                        AND SYSDATE BETWEEN t.offer_from AND t.offer_to'''
        my_query = query_db(oracle_sql)
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



#################################################################################  order master and detial

def ins_outlet_order_mst(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        l_data = request.GET
        l_dic = l_data.dict()
        l_order_date = l_dic['order_date']
        l_outlet_id = l_dic['outlet_id']
        l_route_id = l_dic['route_id']
        l_distributor_id = l_dic['distributor_id']
        l_created_by = l_dic['created_by']
        l_created_dttm = l_dic['created_dttm']
        l_out_order_id = cur_oracle.var(int)
        l_out_order_no = cur_oracle.var(str)
        cur_oracle.callproc("front_end_support_tool.ins_outlet_order_mst",
                            [l_order_date, l_outlet_id, l_route_id, l_distributor_id, l_created_by, l_created_dttm,
                             l_out_order_id, l_out_order_no])
        con.commit()
        l_authentication_result = {"order_id": l_out_order_id.getvalue(), "order_no": l_out_order_no.getvalue()}
        l_json_output = json.dumps(l_authentication_result)
        return HttpResponse(l_json_output)


def upd_outlet_order_mst(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        l_data = request.GET
        l_dic = l_data.dict()
        l_order_id = l_dic['order_id']
        l_order_date = l_dic['order_date']
        l_outlet_id = l_dic['outlet_id']
        l_route_id = l_dic['route_id']
        l_distributor_id = l_dic['distributor_id']
        l_update_by = l_dic['updated_by']
        l_updated_dttm = l_dic['updated_dttm']
        cur_oracle.callproc("front_end_support_tool.upd_outlet_order_mst",
                            [l_order_id, l_order_date, l_outlet_id, l_route_id, l_distributor_id, l_update_by,
                             l_updated_dttm])
        con.commit()
        return HttpResponse(True)


def ins_outlet_order_dtl(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        l_data = request.GET
        l_dic = l_data.dict()
        l_master_id = l_dic['order_id']
        l_item_id = l_dic['item_id']
        l_qty = l_dic['qty']
        l_unit_id = l_dic['unit_id']
        l_rate = l_dic['rate']
        l_amount = l_dic['amount']
        l_status = l_dic['status']
        l_trade_item_id = l_dic['free_with']
        l_created_by = l_dic['created_by']
        l_created_dttm = l_dic['created_dttm']
        cur_oracle.callproc("front_end_support_tool.ins_outlet_order_dtl",
                            [l_master_id, l_item_id, l_qty, l_unit_id, l_rate, l_amount, l_status,l_trade_item_id,l_created_by,
                             l_created_dttm])
        con.commit()
        return HttpResponse(True)

def upd_outlet_order_dtl(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        l_data = request.GET
        l_dic = l_data.dict()
        l_dtl_id = l_dic['order_detail_id']
        l_item_id = l_dic['item_id']
        l_qty = l_dic['qty']
        l_unit_id = l_dic['unit_id']
        l_rate = l_dic['rate']
        l_amount = l_dic['amount']
        l_status = l_dic['status']
        l_trade_item_id = l_dic['free_with']
        l_updated_by = l_dic['updated_by']
        l_updated_dttm = l_dic['updated_dttm']
        cur_oracle.callproc("front_end_support_tool.upd_outlet_order_dtl",
                            [l_dtl_id, l_item_id, l_qty, l_unit_id, l_rate, l_amount, l_status,l_trade_item_id,l_updated_by,
                             l_updated_dttm])
        con.commit()
        return HttpResponse(True)

def del_outlet_order_dtl(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        l_data = request.GET
        l_dic = l_data.dict()
        l_order_detail_id = l_dic['order_detail_id']
        cur_oracle.callproc("front_end_support_tool.del_outlet_order_dtl",
                            [l_order_detail_id])
        con.commit()
        con.close()
        return HttpResponse(True)

def del_outlet_order(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        l_data = request.GET
        l_dic = l_data.dict()
        l_order_id = l_dic['order_id']
        cur_oracle.callproc("front_end_support_tool.del_outlet_order",
                            [l_order_id])
        con.commit()
        con.close()
        return HttpResponse(True)

def query_outlet_order_mst(request):
    if request.method == 'GET':
        l_data = request.GET
        l_dic = l_data.dict()
        l_order_id = l_dic["order_id"]
        oracle_sql = '''SELECT *
                        FROM outlet_order_mst
                        WHERE id = :order_id'''
        my_query = query_db(oracle_sql, {'order_id': l_order_id})
        l_json_output = json.dumps(my_query, default=myconverter)
        return HttpResponse(l_json_output)


def query_outlet_order_dtl(request):
    if request.method == 'GET':
        l_data = request.GET
        l_dic = l_data.dict()
        l_order_id = l_dic["order_id"]
        oracle_sql = '''SELECT *
                        FROM outlet_order_dtl
                        WHERE master_id = :order_id'''
        my_query = query_db(oracle_sql, {'order_id': l_order_id})
        l_json_output = json.dumps(my_query, default=myconverter)
        return HttpResponse(l_json_output)

def query_outlet_order_emp_wise(request):
    if request.method == 'GET':
        l_data = request.GET
        l_dic = l_data.dict()
        l_spo_id = l_dic["spo_id"]
        oracle_sql = '''SELECT oom.order_no,
                               oom.order_date,
                               oi.shop_full_name outlet,
                               smr.route_name route,
                               su.store_unit_name distributor,
                               i.item_name,
                               ood.qty,
                               u.short_name unit_name,
                               ood.rate,
                               ood.amount,
                               oom.outlet_id,
                               ood.status,
                               ood.trade_item_id free_with,
                               ood.item_id,
                               oom.id order_id
                        FROM outlet_order_mst oom,
                             outlet_order_dtl ood,
                             outlet_info oi,
                             sales_market_route smr,
                             store_unit su,
                             item i,
                             unit u
                        WHERE oom.id = ood.master_id(+)
                        AND oom.outlet_id = oi.id(+) 
                        AND oom.route_id = smr.id(+)
                        AND oom.distributor_id = su.pid(+)
                        AND ood.item_id = i.pid(+)
                        AND ood.unit_id = u.pid(+)
                        AND oom.created_by = :p_spo_id'''
        my_query = query_db(oracle_sql, {'p_spo_id': l_spo_id})
        l_json_output = json.dumps(my_query, default=myconverter)
        return HttpResponse(l_json_output)

class query_outlet_order_emp_wise_sr(View):
    def get(self,request):
        if request.method == 'GET':
            l_data = request.GET
            l_dic = l_data.dict()
            for key in l_dic:
                l_spo_id = l_dic[key]
            oracle_sql = '''WITH free_item AS (
                                SELECT ood.id ,
                                       ood.master_id,
                                       ood.item_id free_item_id,
                                       ood.qty,
                                       ood.trade_item_id,
                                       u.short_name free_item_unit,
                                       i.item_name free_item_name
                                FROM outlet_order_dtl ood,
                                     unit u,
                                     item i
                                WHERE ood.unit_id = u.pid(+)
                                AND ood.item_id = i.pid(+)
                                AND ood.status = 'O'
                            )
                            SELECT oom.order_no,
                                   oom.order_date,
                                   oi.shop_full_name outlet,
                                   smr.route_name route,
                                   su.store_unit_name distributor,
                                   i.item_name,
                                   i.pid item_id,
                                   ood.qty,
                                   u.short_name unit_name,
                                   ood.unit_id,
                                   ood.rate,
                                   ood.amount,
                                   oom.outlet_id,
                                   CASE
                                       WHEN free_item.id IS NOT NULL THEN 'Free Item'
                                       ELSE 'None'
                                   END status,
                                   free_item.free_item_id,
                                   free_item.free_item_name,
                                   free_item.qty free_qty,
                                   free_item.free_item_unit
                            FROM outlet_order_mst oom,
                                 outlet_order_dtl ood,
                                 outlet_info oi,
                                 sales_market_route smr,
                                 store_unit su,
                                 item i,
                                 unit u,
                                 free_item
                            WHERE oom.id = ood.master_id(+)
                            AND oom.outlet_id = oi.id(+) 
                            AND oom.route_id = smr.id(+)
                            AND oom.distributor_id = su.pid(+)
                            AND ood.item_id = i.pid(+)
                            AND ood.unit_id = u.pid(+)
                            AND ood.item_id = free_item.trade_item_id(+)
                            AND ood.master_id = free_item.master_id(+)
                            AND ood.status = 'T'
                            AND oom.created_by = :spo_id
                            ORDER BY oom.id'''
            my_query = query_db(oracle_sql, {'spo_id': l_spo_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)

class upd_outlet_order_status(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            l_order_id = l_dic["order_id"]
            cur_oracle.callproc("front_end_support_tool.upd_outlet_order_status",
                                [l_order_id])
            con.commit()
            return HttpResponse(True)

class get_outlet_order_status(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            for key in l_dic:
                l_order_id = l_dic[key]
            l_status = cur_oracle.callfunc('front_end_support_tool.get_order_status', cx_Oracle.STRING, (l_order_id))
            return HttpResponse(l_status)

##################################################################################### delivery master and detail

class ins_outlet_delivery_mst(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            l_delivery_date = l_dic["delivery_date"]
            l_order_id = l_dic["order_id"]
            l_created_by = l_dic["created_by"]
            l_created_dttm = l_dic["created_dttm"]
            l_out_delivery_id = cur_oracle.var(int)
            l_out_delivery_no = cur_oracle.var(str)
            cur_oracle.callproc('front_end_support_tool.ins_outlet_delivery_mst', (l_delivery_date,
                                                                                   l_order_id,
                                                                                   l_created_by,
                                                                                   l_created_dttm,
                                                                                   l_out_delivery_id,
                                                                                   l_out_delivery_no))
            con.commit()
            l_authentication_result = {"delivery_id": l_out_delivery_id.getvalue(), "delivery_no": l_out_delivery_no.getvalue()}
            l_json_output = json.dumps(l_authentication_result)
            return HttpResponse(l_json_output)

class upd_outlet_delivery_mst(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            l_delivery_id = l_dic["delivery_id"]
            l_order_id = l_dic["order_id"]
            l_delivery_no = l_dic["delivery_no"]
            l_delivery_date = l_dic["delivery_date"]
            l_outlet_id = l_dic["outlet_id"]
            l_route_id = l_dic["route_id"]
            l_distributor_id = l_dic["distributor_id"]
            l_updated_by = l_dic["updated_by"]
            l_updated_dttm = l_dic["updated_dttm"]
            cur_oracle.callproc('front_end_support_tool.upd_outlet_delivery_mst' , (l_delivery_id,
                                                                                    l_order_id,
                                                                                    l_delivery_no,
                                                                                    l_delivery_date,
                                                                                    l_outlet_id,
                                                                                    l_route_id,
                                                                                    l_distributor_id,
                                                                                    l_updated_by,
                                                                                    l_updated_dttm))
            con.commit()
            return HttpResponse(True)

class del_outlet_delivery_mst(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            for key in l_dic:
                l_delivery_id = l_dic[key]
            cur_oracle.callproc('front_end_support_tool.del_outlet_delivery_mst', (l_delivery_id))
            con.commit()
            return HttpResponse(True)

class ins_outlet_delivery_dtl(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            l_delivery_id = l_dic["delivery_id"]
            l_item_id = l_dic["item_id"]
            l_qty = l_dic["qty"]
            l_unit_id = l_dic["unit_id"]
            l_unit_name = l_dic["unit_name"]
            l_rate = l_dic["rate"]
            l_amount = l_dic["amount"]
            l_status = l_dic["status"]
            l_created_by = l_dic["created_by"]
            l_created_dttm = l_dic["created_dttm"]
            l_trade_item_id = l_dic["trade_item_id"]
            cur_oracle.callproc('front_end_support_tool.ins_outlet_delivery_dtl', (l_delivery_id,
                                                                                  l_item_id,
                                                                                  l_qty,
                                                                                  l_unit_id,
                                                                                  l_unit_name,
                                                                                  l_rate,
                                                                                  l_amount,
                                                                                  l_status,
                                                                                  l_created_by,
                                                                                  l_created_dttm,
                                                                                  l_trade_item_id)
                               )
            con.commit()
            return HttpResponse(True)

class upd_outlet_delivery_dtl(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            l_delivery_dtl_id = l_dic["delivery_dtl_id"]
            l_item_id = l_dic["item_id"]
            l_qty = l_dic["qty"]
            l_unit_id = l_dic["unit_id"]
            l_unit_name = l_dic["unit_name"]
            l_rate = l_dic["rate"]
            l_amount = l_dic["amount"]
            l_status = l_dic["status"]
            l_updated_by = l_dic["updated_by"]
            l_updated_dttm = l_dic["updated_dttm"]
            l_trade_item_id = l_dic["trade_item_id"]
            cur_oracle.callproc('front_end_support_tool.upd_outlet_delivery_dtl',(l_delivery_dtl_id,
                                                                                  l_item_id,
                                                                                  l_qty,
                                                                                  l_unit_id,
                                                                                  l_unit_name,
                                                                                  l_rate,
                                                                                  l_amount,
                                                                                  l_status,
                                                                                  l_updated_by,
                                                                                  l_updated_dttm,
                                                                                  l_trade_item_id))
            con.commit()
            return HttpResponse(True)

class del_outlet_delivery_dtl(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            for i in l_dic:
                l_delivery_dtl_id = l_dic[i]
            cur_oracle.callproc('front_end_support_tool.del_outlet_delivery_dtl', (l_delivery_dtl_id))
            con.commit()
            return HttpResponse(True)

class del_outlet_delivery(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            for j in l_dic:
                l_delivery_id = l_dic[j]
            cur_oracle.callproc('front_end_support_tool.del_outlet_delivery', (l_delivery_id))
            con.commit()
            return HttpResponse(True)

class query_outlet_delivery_mst(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            for j in l_dic:
                l_delivery_id = l_dic[j]
            oracle_sql = '''SELECT *
                            FROM outlet_delivery_mst
                            WHERE id = :p_delivery_id
                        '''
            my_query = query_db(oracle_sql, {'p_delivery_id': l_delivery_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)

class query_outlet_delivery_dtl(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            for j in l_dic:
                l_delivery_id = l_dic[j]
            oracle_sql = '''SELECT *
                            FROM outlet_delivery_dtl
                            WHERE master_id = :p_delivery_id
                        '''
            my_query = query_db(oracle_sql, {'p_delivery_id': l_delivery_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)

class query_outlet_delivery_emp_wise(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            for j in l_dic:
                l_emp_id = l_dic[j]
            oracle_sql = '''SELECT *
                            FROM outlet_delivery_mst
                            WHERE created_by = :p_emp_id
                         '''
            my_query = query_db(oracle_sql, {'p_emp_id': l_emp_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)

class nested_api(View):
    def get(self,request):
        if request.method == 'GET':
            l_data = request.GET
            l_dic = l_data.dict()
            l_get_json = l_dic["json_object"]
            print(l_get_json)
            return HttpResponse(l_get_json)

class bulk_delivery_ins(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            l_json_string = l_dic["json_object"]
            #l_json = json.dumps(l_json_string)
            l_json_data = json.loads(l_json_string)
            print(type(l_json_data))
            print(l_json_data)
            l_delivery_date = l_json_data["delivery_Date"]
            l_order_id = l_json_data["order_id"]
            l_created_by = l_json_data["createdById"]
            l_created_dttm = l_json_data["created_dttm"]
            l_out_delivery_id = cur_oracle.var(int)
            l_out_delivery_no = cur_oracle.var(str)
            cur_oracle.callproc('front_end_support_tool.ins_outlet_delivery_mst', (l_delivery_date,
                                                                                   l_order_id,
                                                                                   l_created_by,
                                                                                   l_created_dttm,
                                                                                   l_out_delivery_id,
                                                                                   l_out_delivery_no)
                               )
            d = l_json_data
            for i in d:
                if i == 'products':
                    for j in d[i]:
                        for k in j:
                            if k == "item_id":
                                l_item_id = j[k]
                            if k == "qty":
                                l_qty = j[k]
                            if k == "unit_id":
                                l_unit_id = j[k]
                            if k == "unit_name":
                                l_unit_name = j[k]
                            if k == "rate":
                                l_rate = j[k]
                            if k == "amount":
                                l_amount = j[k]
                            if k == "status":
                                l_status = j[k]
                            if k == "freeOfferID":
                                l_trade_item_id = j[k]

                        cur_oracle.callproc('front_end_support_tool.ins_outlet_delivery_dtl', (l_out_delivery_id,
                                                                                               l_item_id,
                                                                                               l_qty,
                                                                                               l_unit_id,
                                                                                               l_unit_name,
                                                                                               l_rate,
                                                                                               l_amount,
                                                                                               l_status,
                                                                                               l_created_by,
                                                                                               l_created_dttm,
                                                                                               l_trade_item_id)
                                            )

            con.commit()
            return HttpResponse(True)

class query_bulk_delivery_data(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            for j in l_dic:
                l_delivery_id = l_dic[j]
            oracle_sql_for_master = ''' SELECT *
                                        FROM outlet_delivery_mst
                                        WHERE id = :p_delivery_id
                                     '''
            my_query = query_db(oracle_sql_for_master, {'p_delivery_id': l_delivery_id})
            l_json_output_1 = json.dumps(my_query, default=myconverter)
            s1 = l_json_output_1[1:len(l_json_output_1)-1]
            l_json_data = json.dumps(s1)
            print(type(l_json_output_1))
            print(l_json_output_1)
            oracle_sql_for_detail =  '''SELECT *
                                        FROM outlet_delivery_dtl
                                        WHERE master_id = :p_delivery_id
                                     '''
            my_query = query_db(oracle_sql_for_detail, {'p_delivery_id': l_delivery_id})
            l_json_output_2 = json.dumps(my_query, default=myconverter)
            list_of_dic = '"DETAIL:"'+l_json_output_2
            l = '{'+str(l_json_output_1[2:len(l_json_output_1)-2]) + ',' + str(list_of_dic)+'}'
            return HttpResponse(l)

class delivery_emp_wise_sr(View):
    def get(self,request):
        if request.method == 'GET':
            l_data = request.GET
            l_dic = l_data.dict()
            for key in l_dic:
                l_spo_id = l_dic[key]
            oracle_sql = '''WITH free_item AS (
                            SELECT ood.id ,
                                   ood.master_id,
                                   ood.item_id free_item_id,
                                   ood.qty,
                                   ood.trade_item_id,
                                   u.short_name free_item_unit,
                                   i.item_name free_item_name
                            FROM outlet_delivery_dtl ood,
                                 unit u,
                                 item i
                            WHERE ood.unit_id = u.pid(+)
                            AND ood.item_id = i.pid(+)
                            AND ood.status = 'O'
                        )
                        SELECT oom.id delivery_id,
                               oom.delivery_no,
                               oom.delivery_date,
                               oi.shop_full_name outlet,
                               smr.route_name route,
                               su.store_unit_name distributor,
                               i.item_name,
                               i.pid item_id,
                               ood.qty,
                               u.short_name unit_name,
                               ood.unit_id,
                               ood.rate,
                               ood.amount,
                               oom.outlet_id,
                               CASE
                                   WHEN free_item.id IS NOT NULL THEN 'Free Item'
                                   ELSE 'None'
                               END status,
                               free_item.free_item_id,
                               free_item.free_item_name,
                               free_item.qty free_qty,
                               free_item.free_item_unit
                        FROM outlet_delivery_mst oom,
                             outlet_delivery_dtl ood,
                             outlet_info oi,
                             sales_market_route smr,
                             store_unit su,
                             item i,
                             unit u,
                             free_item
                        WHERE oom.id = ood.master_id(+)
                        AND oom.outlet_id = oi.id(+) 
                        AND oom.route_id = smr.id(+)
                        AND oom.distributor_id = su.pid(+)
                        AND ood.item_id = i.pid(+)
                        AND ood.unit_id = u.pid(+)
                        AND ood.item_id = free_item.trade_item_id(+)
                        AND ood.master_id = free_item.master_id(+)
                        AND ood.status = 'T'
                        AND oom.created_by = :spo_id'''
            my_query = query_db(oracle_sql, {'spo_id': l_spo_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)


class query_delivery_dtl_sr(View):
    def get(self,request):
        if request.method == 'GET':
            l_data = request.GET
            l_dic = l_data.dict()
            for key in l_dic:
                l_delivery_id = l_dic[key]
            oracle_sql = '''WITH free_item AS (
                            SELECT ood.id ,
                                   ood.master_id,
                                   ood.item_id free_item_id,
                                   ood.qty,
                                   ood.trade_item_id,
                                   u.short_name free_item_unit,
                                   i.item_name free_item_name
                            FROM outlet_delivery_dtl ood,
                                 unit u,
                                 item i
                            WHERE ood.unit_id = u.pid(+)
                            AND ood.item_id = i.pid(+)
                            AND ood.status = 'O'
                        )
                        SELECT oom.id delivery_id,
                               oom.delivery_no,
                               oom.delivery_date,
                               oi.shop_full_name outlet,
                               smr.route_name route,
                               su.store_unit_name distributor,
                               i.item_name,
                               i.pid item_id,
                               ood.qty,
                               u.short_name unit_name,
                               ood.unit_id,
                               ood.rate,
                               ood.amount,
                               oom.outlet_id,
                               CASE
                                   WHEN free_item.id IS NOT NULL THEN 'Free Item'
                                   ELSE 'None'
                               END status,
                               free_item.free_item_id,
                               free_item.free_item_name,
                               free_item.qty free_qty,
                               free_item.free_item_unit
                        FROM outlet_delivery_mst oom,
                             outlet_delivery_dtl ood,
                             outlet_info oi,
                             sales_market_route smr,
                             store_unit su,
                             item i,
                             unit u,
                             free_item
                        WHERE oom.id = ood.master_id(+)
                        AND oom.outlet_id = oi.id(+) 
                        AND oom.route_id = smr.id(+)
                        AND oom.distributor_id = su.pid(+)
                        AND ood.item_id = i.pid(+)
                        AND ood.unit_id = u.pid(+)
                        AND ood.item_id = free_item.trade_item_id(+)
                        AND ood.master_id = free_item.master_id(+)
                        AND ood.status = 'T'
                        AND oom.id = :delivery_id'''
            my_query = query_db(oracle_sql, {'delivery_id': l_delivery_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)

class delivery_query_outlet_wise(View):
    def get(self,request):
        if request.method == 'GET':
            l_data = request.GET
            l_dic = l_data.dict()
            for key in l_dic:
                l_outlet_id = l_dic[key]
            oracle_sql = '''SELECT odm.id delivery_id,
                                   odm.delivery_no,
                                   odm.delivery_date,
                                   oi.shop_full_name outlet_name,
                                   su.store_unit_name distributor_name,
                                   NVL(odm.status,'N') delivery_status
                            FROM outlet_delivery_mst odm,
                                 outlet_info oi,
                                 store_unit su
                            WHERE odm.outlet_id = oi.id
                            AND oi.distributor_id = su.pid(+) 
                            AND outlet_id = :outlet_id
                            ORDER BY odm.delivery_date'''
            my_query = query_db(oracle_sql, {'outlet_id': l_outlet_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)

class product_query_delivery_id_wise(View):
    def get(self,request):
        if request.method == 'GET':
            l_data = request.GET
            l_dic = l_data.dict()
            for key in l_dic:
                l_delivery_id = l_dic[key]
            oracle_sql = '''WITH free_item AS (
                                SELECT ood.id ,
                                       ood.master_id,
                                       ood.item_id free_item_id,
                                       ood.qty,
                                       ood.trade_item_id,
                                       u.short_name free_item_unit,
                                       i.item_name free_item_name
                                FROM outlet_delivery_dtl ood,
                                     unit u,
                                     item i
                                WHERE ood.unit_id = u.pid(+)
                                AND ood.item_id = i.pid(+)
                                AND ood.status = 'O'
                            )
                            SELECT i.item_name,
                                   i.pid item_id,
                                   ood.qty,
                                   u.short_name unit_name,
                                   ood.unit_id,
                                   ood.rate,
                                   ood.amount,
                                   CASE
                                       WHEN free_item.id IS NOT NULL THEN 'Free Item'
                                       ELSE 'None'
                                   END product_status,
                                   NVL(free_item.free_item_id, 0) promotional_id,
                                   NVL(free_item.free_item_id, 0) free_item_id,
                                   NVL(free_item.free_item_name, 'No Data Found') free_item_name, 
                                   NVL(free_item.qty,0) free_qty,
                                   NVL(free_item.free_item_unit, 'No Data Found') free_item_unit 
                            FROM outlet_delivery_mst oom,
                                 outlet_delivery_dtl ood,
                                 outlet_info oi,
                                 sales_market_route smr,
                                 store_unit su,
                                 item i,
                                 unit u,
                                 free_item
                            WHERE oom.id = ood.master_id(+)
                            AND oom.outlet_id = oi.id(+) 
                            AND oom.route_id = smr.id(+)
                            AND oom.distributor_id = su.pid(+)
                            AND ood.item_id = i.pid(+)
                            AND ood.unit_id = u.pid(+)
                            AND ood.item_id = free_item.trade_item_id(+)
                            AND ood.master_id = free_item.master_id(+)
                            AND ood.status = 'T'
                            AND oom.id = :delivery_id'''
            my_query = query_db(oracle_sql, {'delivery_id': l_delivery_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)



#####################################################################################
## IMS (In Market Sales ) BY SMS
#####################################################################################

class bulk_ims_ins(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_query_dict = request.GET
            l_dic = l_query_dict.dict()
            l_string = l_dic["json_object"]
            l_list = ast.literal_eval(l_string)
            print(l_list)
            for dic_object in l_list:
                l_delivery_date = dic_object['ims_date']
                l_delivery_outlet = 0
                l_delivery_sku = 0
                l_dsr = 0
                l_focus_product_ctn = 0
                l_focus_product_memo = dic_object['TFP']
                l_focus_product_sku = 0
                l_lpc = 0
                l_order_outlet = 0
                l_order_sku = dic_object['TSK']
                l_sms_format = dic_object['sms_format']
                l_sms_recv_mobile_no = dic_object['sms_recv_mobile_no']
                l_spo_id = dic_object['spo_id']
                l_timestamp_string = dic_object['timeStamp']
                l_timeStamp = dic_object['timeStamp']
                l_total_delivery_amount = dic_object['TDV']
                l_total_delivery_memo = dic_object['TDM']
                l_total_order_amount = dic_object['TOV']
                l_total_order_memo = dic_object['TOM']
                l_visited_outlet = 0
                l_sms_text = dic_object['sms_text']
                l_out_delivery_mst_id = cur_oracle.var(int)
                l_product_list = dic_object['product_list']
                l_route_total_outlet = dic_object['TOT']
                l_reason_unformatted = dic_object['reason_unformatted']
                l_route_no = dic_object['route']
                cur_oracle.callproc('front_end_support_tool.ins_ims_delivery_mst', (l_delivery_date,
                                                                                    l_spo_id,
                                                                                    l_sms_recv_mobile_no,
                                                                                    l_total_order_amount,
                                                                                    l_total_delivery_amount,
                                                                                    l_order_sku,
                                                                                    l_delivery_sku,
                                                                                    l_focus_product_memo,
                                                                                    l_focus_product_sku,
                                                                                    l_focus_product_ctn,
                                                                                    l_lpc,
                                                                                    l_dsr,
                                                                                    l_visited_outlet,
                                                                                    l_order_outlet,
                                                                                    l_delivery_outlet,
                                                                                    l_total_order_memo,
                                                                                    l_total_delivery_memo,
                                                                                    l_timeStamp,
                                                                                    l_timestamp_string,
                                                                                    l_sms_format,
                                                                                    l_sms_text,
                                                                                    l_spo_id,
                                                                                    l_route_total_outlet,
                                                                                    l_reason_unformatted,
                                                                                    l_route_no,
                                                                                    l_out_delivery_mst_id
                                                                                    )
                                    )
                for elements in l_product_list:
                    print(elements)
                    print(l_out_delivery_mst_id)
                    print(l_spo_id)
                    l_item_code = elements['item_code']
                    l_qty = elements['qty']
                    l_rate = elements['rate']
                    l_amount = elements['amount']
                    print(l_amount)
                    cur_oracle.callproc('front_end_support_tool.ins_ims_delivery_dtl', (
                                                                                            l_out_delivery_mst_id,
                                                                                            l_item_code,
                                                                                            l_qty,
                                                                                            l_rate,
                                                                                            l_amount,
                                                                                            l_spo_id
                                                                                        )
                                        )
                con.commit()
            return HttpResponse(True)

class ins_ims_delivery_sms(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_data = request.GET
            print(l_data)
            l_dic = l_data.dict()
            l_spo_id = l_dic['spo_id']
            l_sms_text = l_dic['sms_text']
            print(l_sms_text)
            l_timestamp = l_dic['timestamp']
            cur_oracle.callproc('front_end_support_tool.ins_ims_delivery_sms', (
                                                                                    l_spo_id,
                                                                                    l_sms_text,
                                                                                    l_timestamp
                                                                                )

                                )
            con.commit()
            return HttpResponse(True)

######################################################################################
## census
######################################################################################

class census_data_process(View):
    def get(self, request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info)
            cur_oracle = con.cursor()
            l_query_dict = request.GET
            l_dic = l_query_dict.dict()
            l_string = l_dic["json_object"]
            l_list = ast.literal_eval(l_string)
            print(l_list)
            l_outlet_info_data = l_list['outlet_info']
            l_area_name = l_outlet_info_data['area_name']
            l_district = l_outlet_info_data['district']
            l_holding_no = l_outlet_info_data['holding_no']
            l_mobile_no = l_outlet_info_data['mobile_no']
            l_outlet_type = l_outlet_info_data['outlet_type']
            l_shop_name = l_outlet_info_data['shop_name']
            l_shop_owner = l_outlet_info_data['shop_owner']
            l_road_no = l_outlet_info_data['road_no']
            l_ward_no = l_outlet_info_data['ward_no']
            l_thana = l_outlet_info_data['thana']
            l_land_mark = l_outlet_info_data['land_mark']
            l_longitude = l_outlet_info_data['longitude']
            l_lattitude = l_outlet_info_data['lattitude']
            l_location_type = l_outlet_info_data['location_type']
            l_out_outlet_id = cur_oracle.var(int)
            cur_oracle.callproc('front_end_support_tool.ins_census_outlet_info', (
                                                                            l_shop_name,
                                                                            l_shop_owner,
                                                                            l_mobile_no,
                                                                            l_holding_no,
                                                                            l_road_no,
                                                                            l_area_name,
                                                                            l_ward_no,
                                                                            l_thana,
                                                                            l_district,
                                                                            l_land_mark,
                                                                            l_longitude,
                                                                            l_lattitude,
                                                                            l_outlet_type,
                                                                            l_location_type,
                                                                            l_out_outlet_id
                                                                            )
                                )
            l_dic_census_mst = l_list['census_mst']
            l_census_date = l_dic_census_mst['census_date']
            l_start_time = l_dic_census_mst['start_time']
            l_end_time = l_dic_census_mst['end_time']
            l_answer_by = l_dic_census_mst['answer_by']
            l_best_company = l_dic_census_mst['best_company']
            l_best_company_representative = l_dic_census_mst['best_company_representative']
            l_deals_with_targeted_prod = l_dic_census_mst['deals_with_targeted_prod']
            l_reason_for_not_dealing = l_dic_census_mst['reason_for_not_dealing']
            l_source_of_purchase = l_dic_census_mst['source_of_purchase']
            l_favourite_comp_1 = l_dic_census_mst['favourite_comp_1']
            l_reason_of_favourite_1 = l_dic_census_mst['reason_of_favourite_1']
            l_favourite_comp_2 = l_dic_census_mst['favourite_comp_2']
            l_reason_of_favourite_2 = l_dic_census_mst['reason_of_favourite_2']
            l_favourite_comp_3 = l_dic_census_mst['favourite_comp_3']
            l_reason_of_favourite_3 = l_dic_census_mst['reason_of_favourite_3']
            l_imei_no = l_dic_census_mst['imei_no']
            l_out_census_mst_id = cur_oracle.var(int)
            cur_oracle.callproc('front_end_support_tool.ins_census_mst', (
                                                                            l_census_date,
                                                                            l_start_time,
                                                                            l_end_time,
                                                                            l_out_outlet_id,
                                                                            l_answer_by,
                                                                            l_deals_with_targeted_prod,
                                                                            l_reason_for_not_dealing,
                                                                            l_source_of_purchase,
                                                                            l_best_company,
                                                                            l_best_company_representative,
                                                                            l_favourite_comp_1,
                                                                            0,
                                                                            l_favourite_comp_2,
                                                                            0,
                                                                            l_favourite_comp_3,
                                                                            0,
                                                                            l_imei_no,
                                                                            l_out_census_mst_id
                                                                          )
                                )
            l_census_dtl_data = l_list['census_data']
            for m in l_census_dtl_data:
                l_company_id = m['company_id']
                l_fiscal_period = m['fiscal_period']
                l_item_type_id = m['item_type_id']
                l_amount = m['amount']
                cur_oracle.callproc('front_end_support_tool.ins_census_dtl', (
                                                                                l_out_census_mst_id,
                                                                                l_fiscal_period,
                                                                                l_company_id,
                                                                                l_item_type_id,
                                                                                l_amount
                                                                             )
                                   )
            con.commit()
            return HttpResponse(True)

###################################################################################################
## spo attendance
###################################################################################################

def user_authentication_rsm(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_user_name = l_dic["user_name"]
        l_pass_word = l_dic["pass_word"]
        l_result = cur_oracle.callfunc('front_end_support_tool.check_login_credential_rsm', cx_Oracle.NUMBER,
                                       (l_user_name, l_pass_word))
        l_emp_id = cur_oracle.callfunc('front_end_support_tool.get_emp_id_rsm', cx_Oracle.NUMBER,
                                       (l_user_name, l_pass_word))
        if l_result == 1:
            oracle_sql = '''WITH rsm AS
                            (
                                SELECT *
                                FROM market_emp
                                WHERE market_pid IN (SELECT pid 
                                                     FROM market
                                                     WHERE upper_no IN (SELECT pid
                                                                        FROM market
                                                                        WHERE upper_no IN (SELECT market_pid 
                                                                                           FROM market_emp
                                                                                           WHERE emp_pid = :p_emp_id
                                                                                           AND transfer_date IS NULL 
                                                                                           AND active_status = 'Y'
                                                                                            )
                                                                        AND market_type_pid = 3)
                                                     AND market_type_pid = 4
                                                     )
                                AND active_status = 'Y'      -- territory
                                UNION
                                SELECT *
                                FROM market_emp
                                WHERE market_pid IN (SELECT pid
                                                     FROM market
                                                     WHERE upper_no IN (SELECT market_pid 
                                                                        FROM market_emp
                                                                        WHERE emp_pid = :p_emp_id
                                                                        AND transfer_date IS NULL 
                                                                        AND active_status = 'Y'
                                                                        )
                                                     AND market_type_pid = 3
                                                     )
                                AND active_status = 'Y'              -- area
                                UNION
                                SELECT * 
                                FROM market_emp
                                WHERE emp_pid = :p_emp_id
                                AND transfer_date IS NULL 
                                AND active_status = 'Y'   -- region (rsm self)
                            )
                            SELECT REGEXP_REPLACE (
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
                                   he.employee_id,
                                   gd.desig_name,
                                   NVL(rsm.area_name,'Not Assigned') area,
                                   NVL(rsm.market_name, 'Not Assigned') territory
                            FROM hrm_employee he,
                                 gbl_desig gd,
                                 rsm
                            WHERE he.employee_id = rsm.emp_pid
                            AND NVL(he.current_desig_id,he.joining_desig_id) = gd.desig_id'''
            my_query = query_db(oracle_sql, {'p_emp_id': l_emp_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)
        else:
            return HttpResponse('Not a valid user !')

def process_rsm_attendance_data(request):
    if request.method == 'GET':
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        l_data = request.GET
        l_emp_list = l_data['att_data']
        l_emp_list = list(l_emp_list)
        print(l_emp_list)
        for i in list(l_emp_list):
            '''cur_oracle.callproc('front_end_support_tool.populate_spo_attendance', (
                i)
            )
        con.commit()'''
            print(i)
        return HttpResponse(True)
        
class dfl_employee_information(View):
    def get(self,request):
        if request.method == 'GET':
            l_data = request.GET
            l_dic = l_data.dict()
            for key in l_dic:
                l_spo_id = l_dic[key]
            oracle_sql = '''SELECT  he.work_mobile,
                                    he.employee_id,
                                    he.auto_formated_id employee_office_id
                                FROM hrm_employee he,
                                    gbl_dept gdept,
                                    gbl_desig gd,
                                    gbl_company gc,
                                    (
                                    SELECT emp_pid,
                                          market_pid,
                                          division_name,
                                          region_name,
                                          area_name,
                                          market_name
                                     FROM market_emp
                                    WHERE active_status = 'Y'
                                    ) me
                                WHERE NVL (he.current_dept_id, he.joining_dept_id) = gdept.dept_id(+)
                                AND NVL (he.current_desig_id, he.joining_desig_id) = gd.desig_id(+)
                                AND NVL (he.current_company_id, he.joining_company_id) = gc.company_id(+)
                                AND he.employee_id = me.emp_pid(+)
                                AND he.employee_category_id IN (4041,4046)
                                AND he.active_ind = 'Y'
                                AND NVL (he.current_company_id, he.joining_company_id) = 1'''
            my_query = query_db(oracle_sql)
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)
            
class ims_v_data(View):
    def get(self,request):
        if request.method == 'GET':
            l_data = request.GET
            l_dic = l_data.dict()
            oracle_sql = '''SELECT * FROM IMS_V WHERE ROWNUM < 101'''
            my_query = query_db(oracle_sql)
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)
            
class region_wise_checker(View):
    def get(self,request):
        if request.method == 'GET':
            l_data = request.GET
            l_dic = l_data.dict()
            l_employee_id = l_dic["employee_id"]
            l_phone_no = l_dic["phone_no"]
            oracle_sql = '''select delivery_date ims_date,
                                   TO_CHAR(delivery_time,'DD/MM/RRRR') delivery_date,
                                   is_formatted,
                                   sms_recv_mobile_no,
                                   timestamp
                            from ims_delivery_mst
                            where 'DFL00'||spo_id = :p_spo_id
                            union all
                            select delivery_date ims_date,
                                   TO_CHAR(delivery_time,'DD/MM/RRRR') delivery_date,
                                   is_formatted,
                                   sms_recv_mobile_no,
                                   timestamp
                            from ims_delivery_mst
                            where sms_recv_mobile_no = :p_mobile_no
                            '''
            my_query = query_db(oracle_sql , {'p_spo_id': l_employee_id, 'p_mobile_no':l_phone_no})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)

class get_ims_sms_for_testing(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info, encoding="utf-8", nencoding="UTF-8")
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            l_initial_status = ''
            l_reason = ''
            l_final_status = ''
            l_out_error_code = ''
            l_out_error_text = ''
            l_out_timestamp = cur_oracle.var(str)
            for key in l_dic:
                l_mobile_no = l_dic["mobile_no"]
                l_timestamp = l_dic["timestamp"]
                l_sms_text = l_dic["sms_text"]
                l_encoded_sms = l_sms_text.encode('utf-8')
                l_decoded_sms = l_encoded_sms.decode('utf-8')
                cur_oracle.callproc('ims_by_sms.ins_ims_by_sms_rcv', (
                    l_mobile_no,
                    l_timestamp,
                    l_decoded_sms,
                    l_initial_status,
                    l_reason,
                    l_final_status,
                    l_out_error_code,
                    l_out_error_text,
                    l_out_timestamp
                )
                                    )
                con.commit()
                return HttpResponse(l_out_timestamp.getvalue())

class reply_ims_sms(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info, encoding="utf-8", nencoding="UTF-8")
            cur_oracle = con.cursor()
            oracle_sql = '''SELECT iv.sms_text,
                                   iv.receiver_no,
                                   iv.sms_outgoing_id
                            FROM      
                            (
                                SELECT gso.sms_text,
                                       gso.receiver_no,
                                       gso.sms_outgoing_id
                                FROM gbl_sms_outgoing gso
                                WHERE gso.sms_status = 'N'
                                ORDER BY gso.sms_outgoing_id
                            ) iv
                            WHERE ROWNUM < 101'''
            my_query = query_db(oracle_sql)
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)

class update_sms_outgoing_status(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info, encoding="utf-8", nencoding="UTF-8")
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            l_out_error_code = cur_oracle.var(str)
            l_out_error_text = cur_oracle.var(str)
            for key in l_dic:
                l_sms_outgoing_id = l_dic[key]
                cur_oracle.callproc('ims_by_sms.upd_gbl_sms_outgoing_status', (
                    l_sms_outgoing_id,
                    l_out_error_code,
                    l_out_error_text
                )
                                    )
                con.commit()
                return HttpResponse(True)

class get_ims_sms(View):
    def get(self,request):
        if request.method == 'GET':
            list_conn_info = get_connection_info_food()
            db_connection_info = str(list_conn_info[0])
            con = cx_Oracle.connect(db_connection_info, encoding="utf-8", nencoding="UTF-8")
            cur_oracle = con.cursor()
            l_data = request.GET
            l_dic = l_data.dict()
            l_initial_status = ''
            l_reason = ''
            l_final_status = ''
            l_out_error_code = ''
            l_out_error_text = ''
            l_out_timestamp = cur_oracle.var(str)
            for key in l_dic:
                l_mobile_no = l_dic["mobile_no"]
                l_timestamp = l_dic["timestamp"]
                l_sms_text = l_dic["sms_text"]
                l_encoded_sms = l_sms_text.encode('utf-8')
                l_decoded_sms = l_encoded_sms.decode('utf-8')
                cur_oracle.callproc('ims_sms_process.ins_ims_by_sms_rcv', (
                    l_mobile_no,
                    l_timestamp,
                    l_decoded_sms,
                    l_initial_status,
                    l_reason,
                    l_final_status,
                    l_out_error_code,
                    l_out_error_text,
                    l_out_timestamp
                )
                                    )
                con.commit()
                return HttpResponse(l_out_timestamp.getvalue())
                #return HttpResponse(True)

