# coding: utf8
import sqlalchemy.exc
import pandas as pd
from dash_table.Format import Format, Group, Scheme, Symbol

def get_main_table(display,form_type, start_date, end_date):
    engine2 = sqlalchemy.create_engine("postgresql://postgres:ahrsDFW34sw@localhost:5432/Dashboards", pool_pre_ping=True)
    not_filed_id = {'f': "('151.1353','151.1354','151.1357','151.1360','153.1394','153.1395','153.1396','153.1397','153.1398')",
    'h':"('195.1682','195.1687','195.1688','195.1692','195.1694','167.1494','167.1499','167.1500','167.1501','167.1502')",
    'g':"('158.1419','158.1420','158.1421','158.1422','158.1423','158.1424','158.1428','158.1430','160.1483','160.1484','160.1485','160.1488','160.1489')",
    'k':"('182.1634','182.1636','184.1639','184.1640','184.1642','184.1645','184.1646','184.1647','184.1655','184.1656')",
    'l':"('200.1712','200.1713','200.1774','201.1715','201.1720','201.1721','201.1723','202.1731','202.1732','202.1734','202.1775')"}
    if display == 'sum':
        sql = f"""
        select 
        form_type as "Название формы"
        ,field_id as "Field_id"
        ,element_name as "Название элемента"
        ,step as "Шаг"
        ,sum(count_session) as "Количество"
        from pixel_session
        where date_insert between '{start_date}' and '{end_date}'
        and form_type = '{form_type}'
        and (field_id is null or field_id not in {not_filed_id[form_type]})
        group by form_type,field_id,element_name,step
        order by step, field_id
        """
        sql_total_session = f"""
        select sum(count_session) as "Количество"
        from pixel_session
        where date_insert between '{start_date}' and '{end_date}'
        and form_type = '{form_type}'
        and (field_id is null or field_id not in {not_filed_id[form_type]})
        and step = '1'
        group by form_type,field_id,element_name,step
        order by step, field_id
        """
        data = pd.read_sql_query(sql, engine2)
        total_session = pd.read_sql_query(sql_total_session, engine2)
        if form_type in ('f', 'h'):
            data.at[3,'Название элемента'] = 'Отчество + Отчество отсутствует'
            data.at[3,'Количество'] = data.at[3,'Количество'] + data.at[4,'Количество']
            data = data.drop([4])
        if form_type in ('l'):
            data.at[7,'Название элемента'] = 'Отчество + Отчество отсутствует'
            data.at[7,'Количество'] = data.at[7,'Количество'] + data.at[8,'Количество']
            data = data.drop([8])

        s = data['Количество'].pct_change()
        s = s.rename("Процент")
        new_data = pd.concat((data,s), axis=1)
        new_data['% от предыдущего шага'] = new_data['Процент'] * (100)
        new_data['% от первого шага'] = new_data['Количество'] / total_session.at[0,'Количество'] * 100
        new_data = new_data.drop('Процент', axis = 1)
        return new_data

    if display == 'by_days':
        sql = f"""
        select date_insert as "Дата"
        , field_id as "Field_id"
        , element_name as "Название элемента"
        , step as "Шаг"
        , count_session as "Количество"
        from pixel_session
        where date_insert between '{start_date}' and '{end_date}'
        and form_type = '{form_type}'
        and (field_id is null or field_id not in {not_filed_id[form_type]})
        order by date_insert,step, field_id
        """
        data = pd.read_sql_query(sql, engine2)
        if form_type in ('f', 'h'):
            data.at[3,'Название элемента'] = 'Отчество + Отчество отсутствует'
            data.at[3,'Количество'] = data.at[3,'Количество'] + data.at[4,'Количество']
            data = data.drop([4])
        return data
    if display == 'by_months':
        sql = f"""
        select 
        TO_CHAR(date_insert, 'yyyy-MM') as "Месяц"
        , case when element_name in ('Начали регистрацию','Закончили регистрацию') then 'null' else field_id end as "Field_id"
        , element_name as "Название элемента"
        , step as "Шаг"
        , sum(count_session) as "Количество"
        from pixel_session
        where date_insert between '{start_date}' and '{end_date}'
        and form_type = '{form_type}'
        and (field_id is null or field_id not in {not_filed_id[form_type]})
        group by TO_CHAR(date_insert, 'yyyy-MM'),field_id,element_name,step
        order by TO_CHAR(date_insert, 'yyyy-MM')
        """
        data = pd.read_sql_query(sql, engine2)
        data = data.pivot_table(values='Количество', index=['Field_id','Название элемента','Шаг'], columns=data['Месяц'], aggfunc='first')
        data.reset_index(inplace=True)
        data.sort_values(by=['Шаг', 'Field_id'], inplace=True)
        return data

def get_engine():
    engine = sqlalchemy.create_engine("mssql+pyodbc://ads.otlnal.ru/OtlNalWork?driver=ODBC+Driver+17+for+SQL+Server?trusted_connection=yes", pool_pre_ping=True)
    engine2 = sqlalchemy.create_engine("postgresql://postgres:ahrsDFW34sw@localhost:5432/Dashboards", pool_pre_ping=True)
    return engine, engine2

def rename_table(data):
    data = data.rename(columns = {"month_":"Месяц","tot_session":"Всего посетителей без PersonID + начатые регистрации","tot_start_reg":"Количество начатых регистраций","conv_reg":"Конверсия","total_start_reg":"Количество начатых регистраций.","tot_end_reg":"Количество успешных регистраций","conv_start_end":"Конверсия.","tot_sesion_again":"Количество сессий","loan_again":"Количество займов","conv_again":".Конверсия"})
    return data

def rename_marketing_funnel(data):
    data = data.rename(columns={'date_insert':'Дата','otlnal_session':'Посетителей otlnal.ru, сессий','get_money_button':'Кнопка Получить деньги, сессий','reg_button':'Кнопка Зарегистрироваться, сессий','total_sc':'Заявок на скоринг','sc_appr':'Одобрено скорингом','cards':'Привязано карт','selfie_appr':'Одобрений селфи','credits':'Выдач'})
    return data

def get_data_table():
    engine, engine2 = get_engine()
    sql = f"""
    select TO_CHAR(date_insert, 'yyyy-MM') as month_
    ,sum(tot_session) as tot_session
    ,sum(tot_start_reg) as tot_start_reg
    ,sum(tot_start_reg)/sum(tot_session)*100 as conv_reg
    ,sum(total_start_reg) as total_start_reg
    ,sum(tot_end_reg) as tot_end_reg
    ,sum(tot_end_reg)/sum(total_start_reg)*100 as conv_start_end
    ,sum(tot_sesion_again) as tot_sesion_again
    ,sum(loan_again) as loan_again
    ,sum(loan_again)/sum(tot_sesion_again)*100 as conv_again
    from conversion_table_days
    group by TO_CHAR(date_insert, 'yyyy-MM')
	order by TO_CHAR(date_insert, 'yyyy-MM')
    """
    data = pd.read_sql_query(sql, engine2) 
    data = rename_table(data)
    return data

def get_data_funnel(form_type, start_date, end_date):
    engine2 = sqlalchemy.create_engine("postgresql://postgres:ahrsDFW34sw@localhost:5432/Dashboards", pool_pre_ping=True)
    not_filed_id = {'f': "('151.1353','151.1354','151.1357','151.1360','153.1394','153.1395','153.1396','153.1397','153.1398')",
    'h':"('195.1682','195.1687','195.1688','195.1692','195.1694','167.1494','167.1499','167.1500','167.1501','167.1502')",
    'g':"('158.1419','158.1420','158.1421','158.1422','158.1423','158.1424','158.1428','158.1430','160.1483','160.1484','160.1485','160.1488','160.1489')",
    'k':"('182.1634','182.1636','184.1639','184.1640','184.1642','184.1645','184.1646','184.1647','184.1655','184.1656')",
    'l':"('200.1712','200.1713','200.1774','201.1715','201.1720','201.1721','201.1723','202.1731','202.1732','202.1734','202.1775')"}
    sql = f"""
        select 
        form_type as "Название формы"
        ,field_id as "Field_id"
        ,case when step = '3' and element_name = 'Кнопка Продолжить' then 'Кнопка Продолжить 2' 
        when field_id = '200.1714' then 'Кнопка Далее 2'
        when field_id = '201.1724' then 'Кнопка Далее 3'
        when field_id = '202.1735' then 'Кнопка Далее 4'
        else element_name end as "Название элемента"
        ,step as "Шаг"
        ,sum(count_session) as "Количество"
        ,case when step = '1' then 'red' 
			when step = '2' then 'orange'
			when step = '3' then 'yellow'
			when step = '4' then 'green'
			when step = '5' then 'blue' else null end as color
        from pixel_session
        where date_insert between '{start_date}' and '{end_date}'
        and form_type = '{form_type}'
        and (field_id is null or field_id not in {not_filed_id[form_type]})
        group by form_type,field_id,element_name,step
        order by step, field_id
        """
    data = pd.read_sql_query(sql, engine2)
    if form_type in ('f', 'h'):
        data.at[3,'Название элемента'] = 'Отчество + Отчество отсутствует'
        data.at[3,'Количество'] = data.at[3,'Количество'] + data.at[4,'Количество']
        data = data.drop([4]) 
    if form_type in ('l'):
            data.at[7,'Название элемента'] = 'Отчество + Отчество отсутствует'
            data.at[7,'Количество'] = data.at[7,'Количество'] + data.at[8,'Количество']
            data = data.drop([8])
    return data['Название элемента'], data['Количество'], data['color']

def get_utm_medium_options(selected_utm_source, start_date, end_date):
    engine_ads, engine_pg = get_engine()
    if len(selected_utm_source)!=0:
        string_utm = "and utm_source in (" + ','.join(["'"+item+"'" for item in selected_utm_source])+")"
    else:
        string_utm=''
    sql = f"""
        select distinct (case when utm_medium is not null then utm_medium else 'Нет' end) as utm_medium
        from funnel_main
        where cast(date_insert as date) between '{start_date}' and '{end_date}'
        {string_utm}
        """   
    df = pd.read_sql(sql, engine_pg)['utm_medium'].to_list()
    options = [{'label': i, 'value': i} for i in df]
    return options

def get_utm_capmaign_options(selected_utm_source,selected_utm_meduim, start_date, end_date):
    engine_ads, engine_pg = get_engine()
    if len(selected_utm_source)!=0:
        string_utm_source = "and utm_source in (" + ','.join(["'"+item+"'" for item in selected_utm_source])+")"
    else:
        string_utm_source=''

    if len(selected_utm_meduim)!=0:
        string_utm_medium = "and utm_source in (" + ','.join(["'"+item+"'" for item in selected_utm_meduim])+")"
    else:
        string_utm_medium=''

    sql = f"""
        select distinct (case when utm_campaign is not null then utm_campaign else 'Нет' end) as utm_campaign
        from funnel_main
        where cast(date_insert as date) between '{start_date}' and '{end_date}'
        {string_utm_source}
        {string_utm_medium}
        """
    df = pd.read_sql(sql, engine_pg)['utm_campaign'].to_list()
    options = [{'label': i, 'value': i} for i in df]
    return options

def get_funnel(start_date, end_date, type_client, utm_source, utm_medium, utm_campaign):
    if len(type_client)!=0:
        type_client_string = "and type_client in (" + ','.join(["'"+item+"'" for item in type_client])+")"
    else:
        type_client_string = ''

    if len(utm_source)!=0:
        utm_source_string = "and utm_source in (" + ','.join(["'"+item+"'" for item in utm_source])+")"
    else:
        utm_source_string = ''

    if len(utm_medium)!=0:
        utm_medium_string = "and utm_medium in (" + ','.join(["'"+item+"'" for item in utm_medium])+")"
    else:
        utm_medium_string = ''
    
    if len(utm_campaign)!=0:
        utm_campaign_string = "and utm_campaign in (" + ','.join(["'"+item+"'" for item in utm_campaign])+")"
    else:
        utm_campaign_string = ''

    engine_ads, engine_pg = get_engine()
    sql = f"""
    select 
    cast(fm.date_insert as varchar) as "Дата"
    ,otlnal as "Сессии"
    ,round(get_money/cast(otlnal as numeric)*100,1) as "CR1"
    ,get_money as "Интерес"
    ,round(reg_button/cast(get_money as numeric)*100,1) as "CR2"
    ,reg_button as "Старт"
    ,round(start_reg/reg_button*100,1) as "CR3"
    ,start_reg as "Контакты"
    ,round(end_reg/start_reg*100,1) as "CR4"
    ,end_reg as "Заврешенные регистрации"
    ,round(sc_approve/end_reg*100,1) as "CR5"
    ,sc_approve as "Одобрения"
    ,round(selfie_approve/sc_approve*100,1) as "CR6"
    ,selfie_approve as "Идентификация"
    ,round(creds_day/selfie_approve*100,1) as "CR7"
    ,creds_day as "Выдача"
    ,sum_cred_day as "Сумма выдач"
    ,round(cast(sum_cred_day/creds_day as numeric),1) as "Средний чек"
    ,round(creds_day/otlnal*100,1) as "CR"
    from
        (select date_insert
        ,case when sum(start_reg)=0 then null else sum(start_reg) end as start_reg
        ,case when sum(end_reg)=0 then null else sum(end_reg) end as end_reg
        ,case when sum(sc_approve)=0 then null else sum(sc_approve) end as sc_approve
        ,case when sum(selfie_approve)=0 then null else sum(selfie_approve) end as selfie_approve
        ,case when sum(creds_day)=0 then null else sum(creds_day) end as creds_day
        ,case when sum(sum_cred_day)=0 then null else sum(sum_cred_day) end as sum_cred_day
        from funnel_main fm
        where date_insert between '{start_date}' and '{end_date}'
        {type_client_string}
        {utm_source_string}
        {utm_medium_string}
        {utm_campaign_string}
        group by date_insert) fm
    left join (select date_insert
            ,case when sum(otlnal)=0 then null else sum(otlnal) end as otlnal
            ,case when sum(get_money)=0 then null else sum(get_money) end as get_money
            ,case when sum(reg_button)=0 then null else sum(reg_button) end as reg_button
            from funnel_session
            where date_insert between '{start_date}' and '{end_date}'
            {utm_source_string}
            {utm_medium_string}
            {utm_campaign_string}
            group by date_insert) fs on fs.date_insert=fm.date_insert
    order by fm.date_insert
    """
    df = pd.read_sql(sql, engine_pg)
    df = df.T.reset_index()
    df = df.rename(columns=df.iloc[0])
    df.drop(df.index[0], inplace = True)
    return df


