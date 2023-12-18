CREATE TABLE DeletedCustomerLog (
    deletionID INT PRIMARY KEY IDENTITY(1,1),
    tc VARCHAR(11),
    name VARCHAR(50),
    surname VARCHAR(50),
    email VARCHAR(50),
    password VARCHAR(50),
    phone VARCHAR(11),
    customerRoleID TINYINT,
    deletionDate DATETIME DEFAULT GETDATE()
);

-- Create the LogDeletedCustomer trigger
CREATE TRIGGER LogDeletedCustomer
ON customer
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO DeletedCustomerLog (tc, name, surname, email, password, phone, customerRoleID)
    SELECT tc, name, surname, email, password, phone, customerRoleID
    FROM deleted;
END;