CREATE TRIGGER update_of_bus_sefer�d
on bus
for update
as
begin
	declare @updatevoyagerouteinserted tinyint
	select @updatevoyagerouteinserted=inserted.voyageRouteID from inserted
	declare @updatevoyageroutedeleted tinyint
	select @updatevoyageroutedeleted=deleted.voyageRouteID from deleted
	print cast(@updatevoyageroutedeleted as varchar(10))+' nolu sefer '+ cast( @updatevoyagerouteinserted as varchar(10))+' nolu sefer olarak g�ncellenmi�tir' 
end