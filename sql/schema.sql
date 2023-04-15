-- schema.sql

# drop database if exists iaos;
create database if not exists iaos;
use iaos;
# grant create,alter ,select, insert, update, delete on iaos.* to 'carl'@'localhost';
# flush privileges;

drop table if exists factor_type;
drop table if exists candidate_factors;
drop table if exists factor_validity_info;

-- 因子类型枚举表
create table if not exists factor_type
(
    id             INT                                  NOT NULL AUTO_INCREMENT comment '因子类型id',
    factor_type_id varchar(10)                          not null comment '因子类型id',
    factor_type    varchar(100)                         not null comment '因子类型',
    create_date    datetime on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP comment '添加日期',
    memo           varchar(500) comment '因子类型备注说明',
    constraint fac_constraint unique (`factor_type_id`),
    PRIMARY KEY (id)
) engine = innodb
  default charset = utf8;

-- 候选因子表
create table if not exists candidate_factors
(
    id             INT                                  NOT NULL AUTO_INCREMENT,
    factor_id      varchar(30)                          not null comment '因子id',
    factor_name    varchar(255)                         not null comment '因子名称',
    factor_type_id varchar(10)                          not null comment '因子类型id',
    factor_type    varchar(100)                         not null comment '因子类型',
    create_date    datetime on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP comment '添加日期',
    memo           varchar(500) comment '因子备注说明',
    constraint fac_constraint unique (`factor_id`),
    key `idx_factor` (`factor_id`),
    PRIMARY KEY (id)
) engine = innodb
  default charset = utf8;

-- 因子有效性信息表
create table if not exists factor_validity_info
(
    id             INT                                  NOT NULL AUTO_INCREMENT,
    factor_id      varchar(30)                          not null comment '因子id',
    factor_name    varchar(255)                         not null comment '因子名称',
    factor_type_id varchar(10)                          not null comment '因子类型id',
    factor_type    varchar(100)                         not null comment '因子类型',
    benchmark      varchar(18)                          not null default '000001.SH' comment '对标基准',
    benchmark_name varchar(30)                          not null default '上证指数' comment '对标基准名称',
    factor_ic      double                               not null default 0.0 comment '年化平均收益与因子的相关性IC(信息比率)',
    total_return   double                               not null default 0.0 comment '因子累积收益',
    annual_return  double                               not null default 0.0 comment '因子年化平均收益',
    excess_return  double                               not null default 0.0 comment '因子超额收益',
    win_prob       double                               not null default 0.0 comment '因子跑赢概率',
    sample_periods int                                  not null default 7 comment '因子有效校验所用数据周期(年)',
    update_date    datetime on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP comment '更新日期',
    memo           varchar(500) comment '备注说明',
    constraint fac_constraint unique (`factor_id`),
    key `idx_factor` (`factor_id`),
    PRIMARY KEY (id)
) engine = innodb
  default charset = utf8;


-- 初始化部分数据表的值
-- 1、因子类型枚举表 factor_type
insert into factor_type (factor_type_id, factor_type, memo)
values ('V_F', '估值因子', '估值因子类型因子');
commit;
insert into factor_type (factor_type_id, factor_type, memo)
values ('G_F', '成长因子', '成长因子类型因子');
commit;
insert into factor_type (factor_type_id, factor_type, memo)
values ('CS_F', '资本结构因子', '资本结构因子类型因子');
commit;
insert into factor_type (factor_type_id, factor_type, memo)
values ('T_F', '技术面因子', '技术面因子类型因子');
commit;
insert into factor_type (factor_type_id, factor_type, memo)
values ('SD_F', '自定义因子', '自定义因子类型因子');
commit;
-- 2、候选因子表 candidate_factors
-- 1、估值因子
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('pe', '市盈率', 'V_F', '估值因子', '市盈率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('pe_ttm', '市盈率TTM', 'V_F', '估值因子', '市盈率TTM');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('pb', '市净率', 'V_F', '估值因子', '市净率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('ps', '市销率', 'V_F', '估值因子', '市销率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('ps_ttm', '市销率TTM', 'V_F', '估值因子', '市销率TTM');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('dv_ratio', '股息率', 'V_F', '估值因子', '股息率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('eps', '基本每股收益', 'V_F', '估值因子', '基本每股收益');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('bps', '每股净资产', 'V_F', '估值因子', '每股净资产');
commit;

-- 2、成长因子
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('roe', '净资产收益率', 'G_F', '成长因子', '净资产收益率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('roe_yearly', '年化净资产收益率', 'G_F', '成长因子', '年化净资产收益率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('npta', '总资产净利润', 'G_F', '成长因子', '总资产净利润');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('roa', '总资产报酬率', 'G_F', '成长因子', '总资产报酬率(资产收益率,资产回报率,=税后净利润/总资产)');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('roa_yearly', '年化总资产净利率', 'G_F', '成长因子', '年化总资产净利率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('roa2_yearly', '年化总资产报酬率', 'G_F', '成长因子', '年化总资产报酬率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('roic', '投入资本回报率', 'G_F', '成长因子', '投入资本回报率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('basic_eps_yoy', '基本每股收益(eps)同比增长率', 'G_F', '成长因子', '基本每股收益(eps)同比增长率(%)');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('op_yoy', '营业利润同比增长率', 'G_F', '成长因子', '营业利润同比增长率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('ebt_yoy', '利润总额同比增长率', 'G_F', '成长因子', '利润总额同比增长率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('tr_yoy', '营业总收入同比增长率', 'G_F', '成长因子', '营业总收入同比增长率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('or_yoy', '营业收入同比增长率', 'G_F', '成长因子', '营业收入同比增长率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('equity_yoy', '净资产同比增长率', 'G_F', '成长因子', '净资产同比增长率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('netprofit_margin', '销售净利率', 'G_F', '成长因子', '销售净利率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('grossprofit_margin', '销售毛利率', 'G_F', '成长因子', '销售毛利率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('profit_to_gr', '净利润率', 'G_F', '成长因子', '净利润率(净利润/营业总收入)');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('op_of_gr', '营业利润率', 'G_F', '成长因子', '营业利润率(营业利润/营业总收入)');
commit;

-- 3、资本结构因子
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('debt_to_assets', '资产负债率', 'CS_F', '资本结构因子', '资产负债率');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('total_mv', '总市值', 'CS_F', '资本结构因子', '总市值');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('circ_mv', '流通市值', 'CS_F', '资本结构因子', '流通市值');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('volume', '成交量', 'CS_F', '资本结构因子', '成交量');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('amount', '成交额', 'CS_F', '资本结构因子', '成交额');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('current_ratio', '流动比率', 'CS_F', '资本结构因子', '流动比率=流动资产合计/流动负债合计');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('quick_ratio', '速动比率', 'CS_F', '资本结构因子', '速动比率=速动资产/流动负债');
commit;

-- 4、技术面因子
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('turnover_rate', '换手率', 'T_F', '技术面因子', '换手率（%）');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('turnover_rate_f', '换手率（自由流通股）', 'T_F', '技术面因子', '换手率（自由流通股）');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('volume_ratio', '量比', 'T_F', '技术面因子', '量比');
commit;
insert into candidate_factors (factor_id, factor_name, factor_type_id, factor_type, memo)
VALUES ('changepercent', '涨跌幅', 'T_F', '技术面因子', '涨跌幅');
commit;