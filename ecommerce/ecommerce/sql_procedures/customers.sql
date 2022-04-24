

CREATE PROCEDURE `get_customer` (customer varchar(50))
BEGIN
	Select C.customer, C.points, U.creation,U.username,U.first_name,U.gender,U.birth_date,U.phone,U.location,U.bio,U.mobile_no,U.user_type 
	from tabUser U
	inner join tabCustomer C on U.name = C.customer
    where U.name = customer;
END
