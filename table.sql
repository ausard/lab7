create database if not exists `test`;

USE `test`;

SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;

/*Table structure for table `test` */

CREATE TABLE IF NOT EXISTS `test` (
  `id` int(11) NOT NULL auto_increment,     
  `name`  varchar(250)  NOT NULL default '',     
  `size`  int(11) NULL,     
  `ext  ` varchar(20) NOT NULL default '',
   PRIMARY KEY  (`id`)
);