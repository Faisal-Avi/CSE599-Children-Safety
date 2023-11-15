"""dekko_group URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
################################# group
from api.views import user_authentication,user_priv ,emp_info,sbu_wise_dept,sbu,attendance,job_card_rpt, query_movement_register,query_movement_register_all,\
                      ins_movement_register,upd_movement_register,del_movement_register,dept_name,late_att_list,late_att_list_detail,get_office_id_card_data,\
                      user_verification,employee_information,attendance_information,employee_job_card,leave_balance_info,user_verify_from_emp_id,late_attendance_list,\
                      day_status , responsibility_handover_to , office_calendar, monthly_canteen_menu, leave_days , token_cancel_request, leave_application

from api.excel_converter import excel_view

################################# canteen
from canteen.views import canteen_today,get_canteen_today_meal,upd_can_token_detail,is_meal_eaten
################################# food
from food.views import food_category_product,query_units,trade_offer,ins_outlet_order_mst,ins_outlet_order_dtl,upd_outlet_order_mst,upd_outlet_order_dtl,\
                       del_outlet_order_dtl,del_outlet_order,query_outlet_order_mst,query_outlet_order_dtl, user_authentication_food, user_priv_food,\
                       query_outlet_order_emp_wise,query_outlet_order_emp_wise_sr,upd_outlet_order_status,get_outlet_order_status,ins_outlet_delivery_mst,upd_outlet_delivery_mst,\
                       del_outlet_delivery_mst,ins_outlet_delivery_dtl,upd_outlet_delivery_dtl,del_outlet_delivery_dtl,del_outlet_delivery,\
                       query_outlet_delivery_mst, query_outlet_delivery_dtl,query_outlet_delivery_emp_wise,bulk_delivery_ins,query_bulk_delivery_data,delivery_emp_wise_sr,\
                       query_delivery_dtl_sr,delivery_query_outlet_wise,product_query_delivery_id_wise,bulk_ims_ins,ins_ims_delivery_sms,census_data_process,\
                       user_authentication_rsm,process_rsm_attendance_data,dfl_employee_information,ims_v_data,region_wise_checker,get_ims_sms,reply_ims_sms,\
                       update_sms_outgoing_status,get_ims_sms_for_testing,info_for_spo
################################# hongbao
from hongbao.views import customer_paid_bill,kitchen_order_taking,kot_fire

from food.excel_converter import region_target,territory_target,national_target,zone_target,area_target,sku_qty_wise_ims,sku_value_wise_ims

urlpatterns = [
    path('admin/', admin.site.urls),
    ########################################################  group
    path('group/api/emp_info', emp_info, name='emp_info'),
    path('group/api/attendance', attendance, name='attendance'),
    path('group/api/job_card_rpt', job_card_rpt, name='job_card_rpt'),
    path('group/api/sbu', sbu, name='sbu'),
    path('group/api/dept', dept_name, name='dept'),
    path('group/api/sbu_wise_dept', sbu_wise_dept, name='sbu_wise_dept'),
    path('group/api/user_authentication', user_authentication, name='user_authentication'),
    path('group/api/user_priv', user_priv, name='user_priv'),
    path('group/api/query_movement_register', query_movement_register, name='query_movement_register'),
    path('group/api/query_movement_register_all', query_movement_register_all, name='query_movement_register_all'),
    path('group/api/ins_movement_register', ins_movement_register, name='ins_movement_register'),
    path('group/api/upd_movement_register', upd_movement_register, name='upd_movement_register'),
    path('group/api/del_movement_register', del_movement_register, name='del_movement_register'),
    path('group/api/late_att_list', late_att_list, name='late_att_list'),
    path('group/api/late_att_list_detail', late_att_list_detail, name='late_att_list_detail'),
    path('group/api/get_office_id_card_data', get_office_id_card_data.as_view(), name='get_office_id_card_data'),
    path('group/api/user_verification', user_verification, name='user_verification'),
    path('group/api/user_verify_from_emp_id', user_verify_from_emp_id, name='user_verify_from_emp_id'),
    path('group/api/employee_information', employee_information, name='employee_information'),
    path('group/api/attendance_information', attendance_information, name='attendance_information'),
    path('group/api/employee_job_card', employee_job_card, name='employee_job_card'),
    path('group/api/leave_balance_info', leave_balance_info, name='leave_balance_info'),
    path('group/api/late_attendance_list', late_attendance_list, name='late_attendance_list'),
    path('group/api/day_status', day_status, name='day_status'),
    path('group/api/responsibility_handover_to', responsibility_handover_to, name='responsibility_handover_to'),
    path('group/api/office_calendar', office_calendar, name='office_calendar'),
    path('group/api/monthly_canteen_menu', monthly_canteen_menu, name='monthly_canteen_menu'),
    path('group/api/leave_days', leave_days, name='leave_days'),
    path('group/api/token_cancel_request', token_cancel_request, name='token_cancel_request'),
    path('group/api/leave_application', leave_application, name='leave_application'),

    path('group/api/excel_view', excel_view, name='excel_view'),

    ######################################################## canteen
    path('canteen/api/canteen_today', canteen_today, name='canteen_today'),
    path('canteen/api/get_canteen_today_meal', get_canteen_today_meal, name='get_canteen_today_meal'),
    path('canteen/api/upd_can_token_detail', upd_can_token_detail, name='upd_can_token_detail'),
    path('canteen/api/is_meal_eaten', is_meal_eaten, name='is_meal_eaten'),

    ######################################################## food
    path('food/api/user_authentication', user_authentication_food, name='user_authentication_food'),
    path('food/api/user_priv', user_priv_food, name='user_priv_food'),
    path('food/api/food_category_product', food_category_product, name='food_category_product'),
    path('food/api/query_units', query_units, name='query_units'),
    path('food/api/trade_offer', trade_offer, name='trade_offer'),
    path('food/api/info_for_spo', info_for_spo, name='info_for_spo'),

    path('food/api/ins_outlet_order_mst', ins_outlet_order_mst, name='ins_outlet_order_mst'),
    path('food/api/ins_outlet_order_dtl', ins_outlet_order_dtl, name='ins_outlet_order_dtl'),
    path('food/api/upd_outlet_order_mst', upd_outlet_order_mst, name='upd_outlet_order_mst'),
    path('food/api/upd_outlet_order_dtl', upd_outlet_order_dtl, name='upd_outlet_order_dtl'),
    path('food/api/del_outlet_order_dtl', del_outlet_order_dtl, name='del_outlet_order_dtl'),
    path('food/api/del_outlet_order', del_outlet_order, name='del_outlet_order'),
    path('food/api/query_outlet_order_mst', query_outlet_order_mst, name='query_outlet_order_mst'),
    path('food/api/query_outlet_order_dtl', query_outlet_order_dtl, name='query_outlet_order_dtl'),
    path('food/api/query_outlet_order_emp_wise', query_outlet_order_emp_wise, name='query_outlet_order_emp_wise'),
    path('food/api/query_outlet_order_emp_wise_sr', query_outlet_order_emp_wise_sr.as_view(), name='query_outlet_order_emp_wise_sr'),
    path('food/api/upd_outlet_order_status', upd_outlet_order_status.as_view() , name='upd_outlet_order_status'),
    path('food/api/get_outlet_order_status', get_outlet_order_status.as_view() , name='get_outlet_order_status'),
    path('food/api/ins_outlet_delivery_mst', ins_outlet_delivery_mst.as_view() , name='ins_outlet_delivery_mst'),
    path('food/api/upd_outlet_delivery_mst', upd_outlet_delivery_mst.as_view() , name='upd_outlet_delivery_mst'),
    path('food/api/del_outlet_delivery_mst', del_outlet_delivery_mst.as_view() , name='del_outlet_delivery_mst'),
    path('food/api/ins_outlet_delivery_dtl', ins_outlet_delivery_dtl.as_view() , name='ins_outlet_delivery_dtl'),
    path('food/api/upd_outlet_delivery_dtl', upd_outlet_delivery_dtl.as_view() , name='upd_outlet_delivery_dtl'),
    path('food/api/del_outlet_delivery_dtl', del_outlet_delivery_dtl.as_view() , name='del_outlet_delivery_dtl'),
    path('food/api/del_outlet_delivery', del_outlet_delivery.as_view() , name='del_outlet_delivery'),
    path('food/api/query_outlet_delivery_mst', query_outlet_delivery_mst.as_view() , name='query_outlet_delivery_mst'),
    path('food/api/query_outlet_delivery_dtl', query_outlet_delivery_dtl.as_view() , name='query_outlet_delivery_dtl'),
    path('food/api/query_outlet_delivery_emp_wise', query_outlet_delivery_emp_wise.as_view() , name='query_outlet_delivery_emp_wise'),
    path('food/api/bulk_delivery_ins', bulk_delivery_ins.as_view() , name='bulk_delivery_ins'),
    path('food/api/query_bulk_delivery_data', query_bulk_delivery_data.as_view(), name='query_bulk_delivery_data'),
    path('food/api/delivery_emp_wise_sr', delivery_emp_wise_sr.as_view(), name='delivery_emp_wise_sr'),
    path('food/api/query_delivery_dtl_sr', query_delivery_dtl_sr.as_view(), name='query_delivery_dtl_sr'),
    path('food/api/delivery_query_outlet_wise', delivery_query_outlet_wise.as_view(), name='delivery_query_outlet_wise'),
    path('food/api/product_query_delivery_id_wise', product_query_delivery_id_wise.as_view(), name='product_query_delivery_id_wise'),
    path('food/api/bulk_ims_ins', bulk_ims_ins.as_view(), name='bulk_ims_ins'),
    path('food/api/ins_ims_delivery_sms', ins_ims_delivery_sms.as_view(), name='ins_ims_delivery_sms'),
    path('food/api/census_data_process', census_data_process.as_view(), name='census_data_process'),
    path('food/api/user_authentication_rsm', user_authentication_rsm, name='user_authentication_rsm'),
    path('food/api/process_rsm_attendance_data', process_rsm_attendance_data, name='process_rsm_attendance_data'), 
    path('food/api/dfl_employee_information', dfl_employee_information.as_view(), name='dfl_employee_information'),
    path('food/api/ims_v_data', ims_v_data.as_view(), name='ims_v_data'), 
    path('food/api/region_wise_checker', region_wise_checker.as_view(), name='region_wise_checker'),
    path('food/api/get_ims_sms', get_ims_sms.as_view(), name='get_ims_sms'),
    path('food/api/reply_ims_sms', reply_ims_sms.as_view(), name='reply_ims_sms'),
    path('food/api/update_sms_outgoing_status', update_sms_outgoing_status.as_view(), name='update_sms_outgoing_status'),
    path('food/api/get_ims_sms_for_testing', get_ims_sms_for_testing.as_view(), name='get_ims_sms_for_testing'),

    path('food/api/region_target', region_target, name='region_target'),
    path('food/api/territory_target', territory_target, name='territory_target'),
    path('food/api/national_target', national_target, name='national_target'),
    path('food/api/zone_target', zone_target, name='zone_target'),
    path('food/api/area_target', area_target, name='area_target'),
    path('food/api/sku_qty_wise_ims', sku_qty_wise_ims, name='sku_qty_wise_ims'),
    path('food/api/sku_value_wise_ims', sku_value_wise_ims, name='sku_value_wise_ims'),

    ############################################################# hongbao
    path('hongbao/api/customer_paid_bill', customer_paid_bill, name='customer_paid_bill'),
    path('hongbao/api/kitchen_order_taking', kitchen_order_taking.as_view(), name='kitchen_order_taking'),
    path('hongbao/api/kot_fire', kot_fire.as_view(), name='kot_fire'),
]
