drop table if exists agencies;
create table agencies
(
    phonenum        varchar(16) not null,
    passwd          varchar(32) default '111111', 
    nickname        varchar(32),
    is_active       boolean default 0,
    money           integer default 0,
    primary key (phonenum)
) engine=InnoDB character set=utf8;


drop table if exists agency_money;
create table agency_money
(
    serial_num     integer unsigned auto_increment,
    phonenum    varchar(16) not null,
    money       integer not null,
    timestamp   datetime default current_timestamp,
    playerid  bigint unsigned not null,
    unique key(serial_num)
) engine = InnoDB character set=utf8;




