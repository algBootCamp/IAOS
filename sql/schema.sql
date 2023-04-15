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
