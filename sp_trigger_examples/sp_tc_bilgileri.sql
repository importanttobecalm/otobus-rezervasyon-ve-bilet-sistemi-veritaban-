CREATE PROCEDURE GetAllTripsForPerson
    @tc VARCHAR(11)
AS
BEGIN
    PRINT 'Start of stored procedure';

    SELECT
        t.ticketID,
        v.voyageID,
        r.routeID,
        c1.cityName AS departureCity,
        r.departurePlatform AS departurePlatform,
        c2.cityName AS arrivalCity,
        r.arrivalPlatform AS arrivalPlatform,
        v.voyageDate,
        v.startTime,
        t.seat,
        p.price
    FROM
        ticket t
        JOIN bus b ON t.busID = b.busID
        JOIN voyage_route vr ON b.voyageRouteID = vr.voyageRouteID
        JOIN voyage v ON vr.voyageID = v.voyageID
        JOIN route r ON vr.routeID = r.routeID
        JOIN city c1 ON r.departure = c1.cityID
        JOIN city c2 ON r.arrival = c2.cityID
        JOIN price p ON t.priceID = p.priceID
    WHERE
        t.tc = @tc
    OPTION (MAXRECURSION 0); -- limiti geçersiz kýlýyor

    PRINT 'End of stored procedure';
END