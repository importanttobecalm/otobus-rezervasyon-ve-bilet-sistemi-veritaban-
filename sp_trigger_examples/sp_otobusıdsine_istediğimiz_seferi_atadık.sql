CREATE PROCEDURE Insert_Bus_and_voyage_route
    @voyageRouteID SMALLINT,
    @busID SMALLINT
AS 
BEGIN
    PRINT 'Start of stored procedure';

    UPDATE bus 
	SET voyageRouteID=@voyageRouteID
	WHERE busID=@busID

    PRINT 'End of stored procedure';
END