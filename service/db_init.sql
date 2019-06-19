CREATE TABLE tasks (
    id			serial PRIMARY KEY,
	md5			varchar(32),
	url			text,
	status		varchar(8)
);