-- EmbeddedQuartzSystemListener check for capitalized table name
-- while everything else does lowercase and postgresql is case
-- sensitive
CREATE TABLE IF NOT EXISTS "QRTZ"
(
	NAME VARCHAR(200) NOT NULL,
	PRIMARY KEY (NAME)
);
