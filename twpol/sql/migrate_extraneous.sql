select (select count(*) from extraneous_voter) + (select count(*) from twpol_voter) "Total voters before";
select count(*) "Num twpol_voter" from twpol_voter;
select count(*) "Num extraneous_voter" from extraneous_voter;
select count(*) "Num voters to move" from twpol_voter where should_process=0;

INSERT extraneous_voter SELECT * FROM twpol_voter where should_process=0;

select count(*) from twpol_voter;
select count(*) from twpol_voter where should_process=0;
select count(*) from extraneous_voter;

DELETE from twpol_voter WHERE should_process=0;

select count(*) "Num errors" from twpol_voter where should_process=0;
select count(*) "Num twpol_voters after" from twpol_voter;
select count(*) "Num extraneous_voters after" from extraneous_voter;
select (select count(*) from extraneous_voter) + (select count(*) from twpol_voter) "Total voters after";