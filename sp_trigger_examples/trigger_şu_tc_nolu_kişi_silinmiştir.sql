create trigger delete_tc
on customer 
for delete
as 
	declare @delete_tc varchar(11)
	select @delete_tc=deleted.tc from deleted
	print cast(@delete_tc as varchar(11))+'tc numaralý kiþi silinmiþtir';



