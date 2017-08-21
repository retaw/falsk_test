drop table if exists agencies;
create table agencies
(
    agencyid        bigint not null,
    superviorid     bigint not null default 0,
    passwd          varchar(32) default '111111', 
    money           integer default 0,
    primary key (agencyid)
) engine=InnoDB character set=utf8;


drop table if exists agency_money;
create table agency_money
(
    serial_num  integer unsigned auto_increment,
    superviorid bigint not null default 0,
    agencyid    bigint,
    playerid    bigint,
    money       integer not null,
    timestamp   datetime default current_timestamp,
    unique key(serial_num)
) engine = InnoDB character set=utf8;



drop table if exists players;
create table players
(
    playerid    bigint not null,
    superviorid bigint default 0,
    timestamp   datetime default current_timestamp,
    unique key(playerid)
) engine = InnoDB character set=utf8;
