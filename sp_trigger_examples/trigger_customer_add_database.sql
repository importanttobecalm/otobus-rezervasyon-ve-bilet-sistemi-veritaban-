CREATE TRIGGER customer_add_database
ON customer
INSTEAD OF INSERT
AS 
BEGIN 
    IF NOT EXISTS (SELECT * FROM customer c INNER JOIN inserted i ON c.tc = i.tc)
		if not exists (SELECT * FROM customer c INNER JOIN inserted i ON c.email = i.email)
		BEGIN
			INSERT INTO customer (tc, name, surname, email, password, phone, customerRoleID)
			SELECT tc, name, surname, email, password, phone, customerRoleID
			FROM inserted;
        
			PRINT 'Kayýt baþarýyla eklendi.';
		END
		ELSE
		BEGIN
			PRINT 'Bu email adresi zaten veritabanýnda mevcut. Kayýt Eklenmedi.';
		END
    ELSE
    BEGIN
        PRINT 'Bu tc numarasý kayýt zaten veritabanýnda mevcut. Kayýt Eklenmedi.';
    END
END;
