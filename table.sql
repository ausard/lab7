/*Table structure for table `test` */

CREATE TABLE IF NOT EXISTS `test` (

  `id` int(11) NOT NULL auto_increment,     
  `filename` varchar(250)  NOT NULL default '',     
  `link`  int(11) NULL,     
  `cilineno` int(11)  NULL,    
  `batchname`  varchar(100) NOT NULL default '',
  `type` varchar(20) NOT NULL default '',    
  `data` varchar(100) NOT NULL default '',
   PRIMARY KEY  (`id`)

);