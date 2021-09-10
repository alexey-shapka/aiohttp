CREATE TABLE IF NOT EXISTS countries (
    country varchar(80) NOT NULL PRIMARY KEY,
    region varchar(20) NOT NULL,
    population integer NOT NULL,
    world_percent float NOT NULL,
    date text,
    source text,
    notes text
);
