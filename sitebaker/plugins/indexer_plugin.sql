create table search (
url varchar(500),
title varchar(500),
search_text tsvector,
actual_text text,
last_modified timestamp);