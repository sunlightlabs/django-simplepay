
Update to 0.2:

	ALTER TABLE simplepay_transaction ADD COLUMN amazon_id varchar(32) NOT NULL DEFAULT '';
	ALTER TABLE simplepay_transaction ADD COLUMN name varchar(128) NOT NULL DEFAULT '';
	ALTER TABLE simplepay_transaction ADD COLUMN email varchar(75) NOT NULL DEFAULT '';
	ALTER TABLE simplepay_transaction ADD COLUMN date_processed datetime;

* add collection of buyer name, buyer email, Amazon transaction ID, and date