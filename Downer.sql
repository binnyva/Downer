CREATE TABLE IF NOT EXISTS `Downer` (
  `id` int(11) unsigned NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  `url` varchar(250) NOT NULL,
  `file_path` varchar(250) NOT NULL,
  `special` varchar(10) NOT NULL,
  `added_on` datetime NOT NULL,
  `downloaded` enum('0','1') default '0',
  `downloaded_on` datetime NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8  ;
