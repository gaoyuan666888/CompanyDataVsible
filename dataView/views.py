# coding=utf-8
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.paginator import Paginator
import json
from RecruitDataVsible import settings
import time
from .models import DialogueRecord
from .models import UserAccount
from .models import BankCase
from .models import Spider
from django.db.models import Q
from django.db.models import F
from django.db.models import Count
from django.forms.models import model_to_dict
import operator
import datetime, pymysql
import xlwt
from io import BytesIO
from dwebsocket.decorators import accept_websocket, require_websocket
from django.db.models import Avg, Max, Min, Count, Sum

clients = {}

TIME = datetime.datetime.now().strftime('%Y-%m-%d')
TIME1 = datetime.datetime.now().strftime('%Y')


def login(request):
    error_msg = ''
    if request.method == "GET":
        return render(request, "login.html")
    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('passwd', None)
        user = UserAccount.objects.filter(jd_name=username).first()
        pwd = UserAccount.objects.get(pwd=password)
        if username == 'hjzd' and pwd:
            request.session['username'] = username
            return redirect('/page/index_i.html')
        elif user and pwd:
            request.session['username'] = username

            return redirect('/page/index_f.html')

        else:
            error_msg = '账号密码或错误'
    return render(request, "login.html", {"error": error_msg})


# request网页请求

# def pageConvert(request, pageName="index_f.html"):
#     jd_name = request.session.get('username', False)
#     user = UserAccount.objects.filter(jd_name=jd_name).first()
#     project_name = user.project_name
#     group_data, business_data = get_group(project_name)
#     return render(request, pageName, locals())


def pageConvert(request, pageName="index_i.html"):
    name = request.session.get('username', False)
    user = UserAccount.objects.filter(jd_name=name).first()
    project_name = user.project_name
    public_media, reply_type = spider_filter(project_name)
    return render(request, pageName, locals())


def getJobInfos(request):

    key_word = {}
    page = request.GET.get("page", 1)
    rows = request.GET.get("rows", 10)
    jd_name = request.session.get('username', False)
    start_time = ' '.join(request.GET.get("start_time", "").split('T'))
    stop_time = ' '.join(request.GET.get("stop_time", "").split('T'))

    key_word["cust_name"] = request.GET.get("cust_name", "")
    key_word["call_type"] = request.GET.get("call_type", "")
    if key_word["call_type"] == '手拨':
        key_word["call_type"] = 1
    elif key_word["call_type"] == '自拨':
        key_word["call_type"] = 0
    elif key_word["call_type"] == '群呼':
        key_word["call_type"] = 3
    else:
        pass
    key_word["fenan_num"] = request.GET.get("fenan_num", "")
    key_word["business_type"] = request.GET.get("business_type", "")
    key_word["group"] = request.GET.get("group", "")
    key_word["start_time"] = start_time
    key_word["stop_time"] = stop_time
    result = getJobsInfoByPageAndRows(jd_name, page, rows, key_word)

    return HttpResponse(json.dumps(result), content_type="application/json")


# 帮助方法
def getJobsInfoByPageAndRows(jd_name, page, rows, key_word):
    user = UserAccount.objects.filter(jd_name=jd_name).first()
    project_name = user.project_name
    infos = DialogueRecord.objects.filter(
        Q(cust_name__icontains=key_word["cust_name"]) & Q(call_type__icontains=key_word["call_type"]) & Q(
            business_type__icontains=key_word["business_type"]) & Q(group__icontains=key_word["group"]) & Q(
            update_time__range=(key_word["start_time"], key_word["stop_time"])) & Q(
            project_name__icontains=project_name))
    paginator = Paginator(infos, rows)
    query_sets = paginator.page(page)
    dic_query = query_sets.object_list.values()
    # 展示信息列表
    show_infos = []
    lt_infos = []
    cust_names = []   #坐席姓名
    for item in dic_query:
        cust_names.append(item['cust_name'])
        item['update_time'] = item['update_time'].strftime('%Y-%m-%d %H:%M:%S')
        lt_infos.append(item)

    # 回退，分案查询
    stop_time = key_word['stop_time']
    time_lt = stop_time.split('-')
    year = time_lt[0]
    month = time_lt[1]
    new_time = year + '-' + month + '-' + '01' + ' 00:00:00'
    bank_case = BankCase.objects.filter(Q(cas_ins_time__range=(new_time, stop_time)) & Q(project_name=project_name))
    lt_bc = []
    for bc in bank_case.values():
        lt_bc.append(bc)
    for name in list(set(cust_names)):
        cust_info = {}
        cust_info['cust_name'] = name
        cust_info['fenan_num'] = 0  # 分案数量
        cust_info['ht_case'] = 0  # 回退案件
        cust_info['fa_sum_money'] = 0  # 分案金额
        cust_info['ht_money'] = 0  # 回退金额
        cust_info['call_sum'] = 0  # 拨打量
        cust_info['pass_sum'] = 0  # 接通量
        cust_info['call_time'] = 0  # 通话时长
        cust_info['pass_rate'] = 0  # 接通率
        cust_info['all_sum'] = 0  # 群呼量
        cust_info['all_pass'] = 0  # 群呼接通量
        cust_info['all_time'] = 0  # 群呼时长
        cust_info['all_pass_rate'] = 0  # 群呼接通率
        try:
            for item in lt_infos:
                if item['cust_name'] == name:
                    # 计算分案数量，分案金额，会退数量，回退金额
                    for item1 in lt_bc:
                        if item['cust_name'] == item1['cust_name'] and item['project_name'] == item1['project_name']:
                            if item1['cas_state'] == 1 or item1['cas_state'] == 3:
                                cust_info['fenan_num'] += 1
                            if item1['cas_state'] == 3:
                                cust_info['ht_case'] += 1
                            if item1['cas_state'] == 1 or item1['cas_state'] == 3:
                                cust_info['fa_sum_money'] += item1['cas_m']
                            if item1['cas_state'] == 3:
                                cust_info['ht_money'] += item1['cas_m']
                        else:
                            pass

                    # 拨打量, 群呼量计算
                    if item['call_type'] == 0:
                        cust_info['call_type'] = '自拨'
                        cust_info['call_sum'] += 1

                    if item['call_type'] == 1:
                        cust_info['call_type'] = '手拨'
                        cust_info['call_sum'] += 1
                    if item['call_type'] == 2:
                        cust_info['call_type'] = '话机拨'
                        cust_info['call_sum'] += 1
                    if item['call_type'] == 3:
                        cust_info['call_type'] = '群呼'
                        cust_info['call_sum'] += 1
                        cust_info['all_sum'] += 1
                    else:
                        pass

                    # 接通量，群呼接通量, 总通话时长计算
                    if item['answer_type'] == 0:
                        cust_info['pass_sum'] += 1
                        cust_info['all_pass'] += 1
                        cust_info['call_time'] = round((cust_info['call_time'] + item['dialogue_duration']) / 60, 2)
                    # 群呼通话时长
                    if item['call_type'] == 3 and item['answer_type'] == 0:
                        cust_info['all_time'] = round((cust_info['all_time'] + item['dialogue_duration']) / 60, 2)
                    # 接通率， 群呼接通率
                    cust_info['pass_rate'] = round(cust_info['pass_sum'] / cust_info['call_sum'], 3)
                    cust_info['all_pass_rate'] = round(cust_info['all_pass'] / cust_info['all_sum'], 3)
                    if cust_info['create_time']:
                        cust_info['create_time'] = item['create_time'].strftime('%Y-%m-%d %H:%M:%S')
                    if cust_info['answer_time']:
                        cust_info['answer_time'] = item['answer_time'].strftime('%Y-%m-%d %H:%M:%S')
                    if cust_info['hangup_time']:
                        cust_info['hangup_time'] = item['hangup_time'].strftime('%Y-%m-%d %H:%M:%S')
                    if cust_info['fa_sum_money']:
                        cust_info['fa_sum_money'] = str(item['fa_sum_money'])
                    if cust_info['ht_money']:
                        cust_info['ht_money'] = str(item['ht_money'])
                    #分组
                    cust_info['group'] = item['group']
        except:
            pass
        show_infos.append(cust_info)

    # for item in lt_infos:
    #     new_time = item['update_time']
    #     # print(new_time, type(new_time))
    #     # item['create_time'] = new_time.strftime('%Y-%m-%d')
    #     item['create_time'] = item['create_time'].strftime('%Y-%m-%d %H:%M:%S')
    #     item['answer_time'] = item['answer_time'].strftime('%Y-%m-%d %H:%M:%S')
    #     item['hangup_time'] = item['hangup_time'].strftime('%Y-%m-%d %H:%M:%S')
    #     item['fa_sum_money'] = str(item['fa_sum_money'])
    #     item['ht_money'] = str(item['ht_money'])
    #     # item['call_time'] = item['call_time'].strftime('%Y-%m-%d %H:%M:%S')
    #     for case in lt_bc:
    #         if item['project_name'] == case['project_name'] and item['cust_name'] == case['cust_name']:
    #             pass
    #         pass
    return {"total": paginator.count, "rows": show_infos}


def get_group(jd_name):
    group_data = []
    business_data = []
    db = pymysql.connect("localhost", "root", "123456", "hj_bi", charset='utf8mb4')
    cursor = db.cursor()
    group_sql = ''' select `group` from dialogue_record where project_name=%s ''' % jd_name
    business_sql = ''' select business_type from dialogue_record where project_name=%s ''' % jd_name
    cursor.execute(group_sql)
    groups = cursor.fetchall()
    cursor.execute(business_sql)
    business = cursor.fetchall()
    lt_group = []
    lt_business = []
    for i in groups:
        lt_group.append(i[0])
    for item in business:
        lt_business.append(item[0])
    for j in set(lt_group):
        group_data.append(j)
    for k in set(lt_business):
        business_data.append(k)
    return group_data, business_data


def spider_filter(project):
    public_media = []
    reply_type = []
    db = pymysql.connect("localhost", "root", "123456", "hj_bi", charset='utf8mb4')
    cursor = db.cursor()
    public_sql = ''' select `public_media` from spider where project_name='%s' ''' % project
    reply_sql = ''' select `reply_type` from spider where project_name='%s' ''' % project
    cursor.execute(public_sql)
    publics = cursor.fetchall()
    cursor.execute(reply_sql)
    replys = cursor.fetchall()
    lt_group = []
    lt_business = []
    for i in publics:
        lt_group.append(i[0])
    for item in replys:
        lt_business.append(item[0])
    for j in set(lt_group):
        public_media.append(j)
    for k in set(lt_business):
        reply_type.append(k)
    return public_media, reply_type


def getSpiderInfo(request):
    key_word = {}
    page = request.GET.get("page", 1)
    rows = request.GET.get("rows", 10)
    jd_name = request.session.get('username', False)
    start_time = ' '.join(request.GET.get("start_time", "").split('T'))
    stop_time = ' '.join(request.GET.get("stop_time", "").split('T'))
    key_word["title"] = request.GET.get("title", "")
    key_word["public_media"] = request.GET.get("public_media", "")
    key_word["reply_type"] = request.GET.get("reply_type", "")
    key_word["start_time"] = start_time
    key_word["stop_time"] = stop_time
    result = getSpiderInfoByPageAndRows(jd_name, page, rows, key_word)
    return HttpResponse(json.dumps(result), content_type="application/json")


#展示舆论信息
def getSpiderInfoByPageAndRows(jd_name, page, rows, key_word):
    user = UserAccount.objects.filter(jd_name=jd_name).first()
    project_name = user.project_name
    infos = Spider.objects.filter(
        Q(public_media__icontains=key_word["public_media"]) & Q(reply_type__icontains=key_word["reply_type"]) & (Q(title__icontains=key_word['title']) | Q(reply_content__icontains=key_word['title']) | Q(second_reply__icontains=key_word['title']) | Q(content__icontains=key_word['title']))
        & (Q(public_time__range=(key_word["start_time"], key_word["stop_time"])) | Q(reply_time__range=(key_word["start_time"], key_word["stop_time"]))) & Q(
            project_name__icontains=project_name))
    paginator = Paginator(infos, rows)
    query_sets = paginator.page(page)
    dic_query = query_sets.object_list.values()
    print(dic_query)
    show_infos = []
    for item in dic_query:
        try:
            item['public_time'] = item['public_time'].strftime('%Y-%m-%d %H:%M:%S')
            item['reply_time'] = item['reply_time'].strftime('%Y-%m-%d %H:%M:%S')
            show_infos.append(item)
        except:
            pass

    return {"total": paginator.count, "rows": show_infos}

#舆论趋势
def getReplyTypeCountByTime(request):
    year = request.GET.get("year", "2019")
    if year == '':
        year = TIME1
    result = {}
    r_types = []
    l_types = []
    m_types = []
    public_medias = []
    count_ids = []
    db = pymysql.connect("localhost", "root", "123456", "hj_bi", charset='utf8mb4')
    cursor = db.cursor()
    public_sql = ''' SELECT DATE_FORMAT(public_time,'%Y-%m') as month, content_type,COUNT(content_type), public_media from spider WHERE
                    DATE_FORMAT(public_time,'%Y') = {}  GROUP BY month,content_type  ORDER BY month '''.format(year)
    reply_sql = ''' SELECT DATE_FORMAT(reply_time,'%Y-%m') as month, reply_type,COUNT(reply_type), public_media from spider WHERE 
                    DATE_FORMAT(reply_time,'%Y') = {}  GROUP BY month, reply_type ORDER BY month '''.format(year)

    cursor.execute(public_sql)
    p_datas = cursor.fetchall()   #发布内容类型数据： 2019-07	中性	3
    cursor.execute(reply_sql)
    r_datas = cursor.fetchall()  # 回复内容类型数据： 2019-07	中性	3
    dates = []
    for i in p_datas:
        dates.append(i[0])
    for j in r_datas:
        dates.append(j[0])
    months = sorted(list(set(dates)), reverse=False)
    for month in months:
        r_count = 0
        l_count = 0
        m_count = 0
        #发布内容类型
        for data in p_datas:
            if data[0] == month:
                if data[1] == "正面":
                    r_count += data[2]
                if data[1] == "负面":
                    l_count += data[2]
                if data[1] == "中性":
                    m_count += data[2]
        #回复内容类型
        for item in r_datas:
            if item[0] == month:
                if item[1] == '正面':
                    r_count += item[2]
                if item[1] == '负面':
                    l_count += item[2]
                if item[1] == '中性':
                    m_count += item[2]
        r_types.append(r_count)
        l_types.append(l_count)
        m_types.append(m_count)

    result["names"] = months
    result["counts"] = count_ids
    result['public_medias'] = public_medias
    result['r_types'] = r_types
    result['l_types'] = l_types
    result['m_types'] = m_types

    return HttpResponse(json.dumps(result), content_type="application/json")



def getEducationAndExperienceOfCity(request):
    result = {}

    postType = request.GET.get("post_type", "")
    # r_count = list((Spider.objects.filter(Q(public_media__icontains=postType) & Q(content_type__icontains="正面")).aggregate(r_count=Count('content_type'))).values())[0]
    # l_count = list((Spider.objects.filter(Q(public_media__icontains=postType) & Q(content_type__icontains="负面")).aggregate(r_count=Count('content_type'))).values())[0]
    # m_count = list((Spider.objects.filter(Q(public_media__icontains=postType) & Q(content_type__icontains="中性")).aggregate(r_count=Count('content_type'))).values())[0]
    r_count = Spider.objects.filter(Q(public_media__icontains=postType) & Q(content_type__icontains="正面")).aggregate(正面=Count('content_type'))
    l_count = Spider.objects.filter(Q(public_media__icontains=postType) & Q(content_type__icontains="负面")).aggregate(负面=Count('content_type'))
    m_count = Spider.objects.filter(Q(public_media__icontains=postType) & Q(content_type__icontains="中性")).aggregate(中性=Count('content_type'))
    print(r_count, l_count, m_count)
    lt_type = ['正面', '负面', '中性']
    dic_r = {}
    dic_l = {}
    dic_m = {}

    dic_r['name'] = list(r_count.keys())[0]
    dic_r['value'] = list(r_count.values())[0]

    dic_l['name'] = list(l_count.keys())[0]
    dic_l['value'] = list(l_count.values())[0]

    dic_m['name'] = list(m_count.keys())[0]
    dic_m['value'] = list(m_count.values())[0]
    count_reply = []
    count_reply.append(dic_r)
    count_reply.append(dic_l)
    count_reply.append(dic_m)
    result['seriesData'] = count_reply
    result['legendData'] = lt_type
    print(result)
    return HttpResponse(json.dumps(result), content_type="application/json")

