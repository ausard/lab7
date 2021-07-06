CREATE DATABASE images;
use images;

CREATE TABLE IF NOT EXISTS images (
  id int NOT NULL AUTO_INCREMENT PRIMARY KEY,     
  name  varchar(250)  NOT NULL default '',
  date  varchar(250) NOT NULL default '',
  size  int ,     
  ext varchar(200) NOT NULL default ''
);
