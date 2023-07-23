SET client_encoding = 'UTF8';
drop  table test.rusrs;

create table test.rusrs(
                 iduser   SERIAL PRIMARY KEY,
                 firstname varchar(35) NULL,
                 lastname  varchar(35) NULL,
                 login    varchar(35) NULL,
                 email    varchar(35) NULL,
                 phone    varchar(15) NULL,
                 status   varchar(1) NOT NULL default 'O',
                 dtopen   date  not null default now() ,
                 dtclose  date ,
                 idt      date  not null default now() ,
                 itm      time  not null default now(),
                 mdt      date NULL ,
                 mtm      time NULL

) ;

CREATE INDEX rusers_email_idx
    ON test.rusrs USING btree
    (email ASC NULLS LAST)
;

CREATE INDEX rusers_phone_idx
    ON test.rusrs USING btree
    (phone ASC NULLS LAST)
;

CREATE INDEX rusers_login_idx
    ON test.rusrs USING btree
    (login ASC NULLS LAST)
;

