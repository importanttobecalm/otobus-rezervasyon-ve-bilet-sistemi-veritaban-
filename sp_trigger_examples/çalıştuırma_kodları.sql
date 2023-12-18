
----sp place
--EXEC GetAllTripsForPerson @tc = '1';
--EXEC search_for_name @name = '1';
--EXEC search_for_surname @surname = '1';
--EXEC search_for_surname_and_name @surname = '1', @name='1';
--EXEC search_customer_with_tc @tc= '1';
EXEC Insert_Bus_and_voyage_route @voyageRouteID=2 , @busID= 1;



-- tricker place
--DELETE FROM customer
--WHERE tc = '5';


--DELETE FROM customer
--WHERE tc = '7';


--DELETE FROM customer
--WHERE tc = '8';
--select * from customer;
--DELETE FROM customer WHERE tc = '4';

