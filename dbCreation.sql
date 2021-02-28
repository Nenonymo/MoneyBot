CREATE TABLE `Servers` (
  `id` varchar(18) PRIMARY KEY,
  `name` varchar(255),
  `prefix` varchar(1) COMMENT 'default=$'
);

CREATE TABLE `Users` (
  `id` varchar(18) PRIMARY KEY,
  `InterractionsAmount` int,
  `name` varchar(128)
);

CREATE TABLE `UserServer` (
  `ServerID` varchar(18),
  `UserID` varchar(18),
  `MoneyAmount` bigint,
  `BotAdmin` tinyint(1),
  `InterractionsAmount` Int,
  PRIMARY KEY (`ServerID`, `UserID`)
);

CREATE TABLE `commands` (
  `id` int PRIMARY KEY,
  `Alias` str
);

CREATE TABLE `CommandServer` (
  `CommandID` int,
  `ServerID` varchar(18),
  `Authorized` tinyint(1),
  PRIMARY KEY (`CommandID`, `ServerID`)
);

CREATE TABLE `Work` (
  `serverID` varchar(18) PRIMARY KEY,
  `channelID` varchar(18),
  `amount` tinyint
);

ALTER TABLE `CommandServer` ADD FOREIGN KEY (`CommandID`) REFERENCES `commands` (`id`);

ALTER TABLE `CommandServer` ADD FOREIGN KEY (`ServerID`) REFERENCES `Servers` (`id`);

ALTER TABLE `UserServer` ADD FOREIGN KEY (`ServerID`) REFERENCES `Servers` (`id`);

ALTER TABLE `UserServer` ADD FOREIGN KEY (`UserID`) REFERENCES `Users` (`id`);

ALTER TABLE `Work` ADD FOREIGN KEY (`serverID`) REFERENCES `Servers` (`id`);

