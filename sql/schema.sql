-- schema.sql

# drop database if exists iaos;
create database if not exists iaos;
use iaos;
# grant create,alter ,select, insert, update, delete on iaos.* to 'carl'@'localhost';
# flush privileges;

-- 候选因子表
create table if not exists candidate_factors(
    id INT NOT NULL AUTO_INCREMENT comment '因子id',
    factor varchar(50) not null comment '因子',
    factor_name varchar(255) not null comment '因子名称',
    factor_type varchar(100) not null comment '因子类型',
    create_date DATE comment '添加日期',
    memo varchar(500) comment '因子备注说明',
    constraint fac_constraint unique (`factor`),
    key `idx_factor` (`factor`),
    PRIMARY KEY (id)
)engine=innodb default charset=utf8;