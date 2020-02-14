DROP TABLE IF EXISTS animals;
CREATE TABLE animals (id int primary key, name text, species text);
INSERT INTO animals VALUES
    (1, 'Bob', 'Llama'),
    (2, 'Jim', 'Lemur'),
    (3, 'Franklin', 'Donkey'),
    (4, 'Tim', 'Mouse'),
    (5, 'Joe', 'Elephant'),
    (6, 'Matt', 'Monkey'),
    (7, 'Mark', 'Lemur'),
    (8, 'Roscoe', 'Lemur'),
    (9, 'Laurel', 'Llama'),
    (10, 'David', 'Monkey')
;


DROP TABLE IF EXISTS users;
CREATE TABLE users (id int primary key, email text, api_key text);
INSERT INTO users VALUES
    (1, 'aaa@gmail.com', 'blah'),
    (2, 'bbbb@yahoo.com', 'blahblah'),
    (3, 'ccccccc@outlook.com', 'blabbityblah')
;