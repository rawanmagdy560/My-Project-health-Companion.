-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: health_companion
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `sports_data`
--

DROP TABLE IF EXISTS `sports_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sports_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sport_type` varchar(120) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `videos` text COLLATE utf8mb4_general_ci,
  `timestamp` varchar(120) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_sports_user` (`user_id`),
  CONSTRAINT `fk_sports_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sports_data`
--

LOCK TABLES `sports_data` WRITE;
/*!40000 ALTER TABLE `sports_data` DISABLE KEYS */;
INSERT INTO `sports_data` VALUES (1,'اليوغا','[{\"title\": \"\\u064a\\u0648\\u063a\\u0627 \\u0635\\u0628\\u0627\\u062d\\u064a\\u0629 \\u0628\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\", \"description\": \"\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0639\\u0631\\u0636 \\u0642\\u0627\\u0626\\u0645\\u0629 \\u0641\\u064a\\u062f\\u064a\\u0648\\u0647\\u0627\\u062a \\u0639\\u0631\\u0628\\u064a\\u0629 \\u062d\\u0648\\u0644 \\u0647\\u0630\\u0627 \\u0627\\u0644\\u062a\\u0645\\u0631\\u064a\\u0646.\", \"video_id\": null, \"thumbnail\": null, \"channel_title\": \"\\u064a\\u0648\\u062a\\u064a\\u0648\\u0628\", \"video_url\": \"https://www.youtube.com/results?search_query=%D9%8A%D9%88%D8%BA%D8%A7+%D8%B5%D8%A8%D8%A7%D8%AD%D9%8A%D8%A9+%D8%A8%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A\"}, {\"title\": \"\\u064a\\u0648\\u063a\\u0627 \\u0644\\u0644\\u0627\\u0633\\u062a\\u0631\\u062e\\u0627\\u0621 \\u0628\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\", \"description\": \"\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0639\\u0631\\u0636 \\u0642\\u0627\\u0626\\u0645\\u0629 \\u0641\\u064a\\u062f\\u064a\\u0648\\u0647\\u0627\\u062a \\u0639\\u0631\\u0628\\u064a\\u0629 \\u062d\\u0648\\u0644 \\u0647\\u0630\\u0627 \\u0627\\u0644\\u062a\\u0645\\u0631\\u064a\\u0646.\", \"video_id\": null, \"thumbnail\": null, \"channel_title\": \"\\u064a\\u0648\\u062a\\u064a\\u0648\\u0628\", \"video_url\": \"https://www.youtube.com/results?search_query=%D9%8A%D9%88%D8%BA%D8%A7+%D9%84%D9%84%D8%A7%D8%B3%D8%AA%D8%B1%D8%AE%D8%A7%D8%A1+%D8%A8%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A\"}]','2025-11-15T01:07:08.872646',3),(2,'تمارين القوة','[{\"title\": \"\\u062a\\u0645\\u0627\\u0631\\u064a\\u0646 \\u0627\\u0644\\u0642\\u0648\\u0629 \\u0627\\u0644\\u0645\\u0646\\u0632\\u0644\\u064a\\u0629 \\u0628\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\", \"description\": \"\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0639\\u0631\\u0636 \\u0642\\u0627\\u0626\\u0645\\u0629 \\u0641\\u064a\\u062f\\u064a\\u0648\\u0647\\u0627\\u062a \\u0639\\u0631\\u0628\\u064a\\u0629 \\u062d\\u0648\\u0644 \\u0647\\u0630\\u0627 \\u0627\\u0644\\u062a\\u0645\\u0631\\u064a\\u0646.\", \"video_id\": null, \"thumbnail\": null, \"channel_title\": \"\\u064a\\u0648\\u062a\\u064a\\u0648\\u0628\", \"video_url\": \"https://www.youtube.com/results?search_query=%D8%AA%D9%85%D8%A7%D8%B1%D9%8A%D9%86+%D8%A7%D9%84%D9%82%D9%88%D8%A9+%D8%A7%D9%84%D9%85%D9%86%D8%B2%D9%84%D9%8A%D8%A9+%D8%A8%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A\"}, {\"title\": \"\\u062a\\u0645\\u0627\\u0631\\u064a\\u0646 \\u0648\\u0632\\u0646 \\u0627\\u0644\\u062c\\u0633\\u0645 \\u0628\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\", \"description\": \"\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0639\\u0631\\u0636 \\u0642\\u0627\\u0626\\u0645\\u0629 \\u0641\\u064a\\u062f\\u064a\\u0648\\u0647\\u0627\\u062a \\u0639\\u0631\\u0628\\u064a\\u0629 \\u062d\\u0648\\u0644 \\u0647\\u0630\\u0627 \\u0627\\u0644\\u062a\\u0645\\u0631\\u064a\\u0646.\", \"video_id\": null, \"thumbnail\": null, \"channel_title\": \"\\u064a\\u0648\\u062a\\u064a\\u0648\\u0628\", \"video_url\": \"https://www.youtube.com/results?search_query=%D8%AA%D9%85%D8%A7%D8%B1%D9%8A%D9%86+%D9%88%D8%B2%D9%86+%D8%A7%D9%84%D8%AC%D8%B3%D9%85+%D8%A8%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A\"}]','2025-11-29T22:23:59.019195',6),(3,'تمارين القوة','[{\"title\": \"\\u062a\\u0645\\u0627\\u0631\\u064a\\u0646 \\u0627\\u0644\\u0642\\u0648\\u0629 \\u0627\\u0644\\u0645\\u0646\\u0632\\u0644\\u064a\\u0629 \\u0628\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\", \"description\": \"\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0639\\u0631\\u0636 \\u0642\\u0627\\u0626\\u0645\\u0629 \\u0641\\u064a\\u062f\\u064a\\u0648\\u0647\\u0627\\u062a \\u0639\\u0631\\u0628\\u064a\\u0629 \\u062d\\u0648\\u0644 \\u0647\\u0630\\u0627 \\u0627\\u0644\\u062a\\u0645\\u0631\\u064a\\u0646.\", \"video_id\": null, \"thumbnail\": null, \"channel_title\": \"\\u064a\\u0648\\u062a\\u064a\\u0648\\u0628\", \"video_url\": \"https://www.youtube.com/results?search_query=%D8%AA%D9%85%D8%A7%D8%B1%D9%8A%D9%86+%D8%A7%D9%84%D9%82%D9%88%D8%A9+%D8%A7%D9%84%D9%85%D9%86%D8%B2%D9%84%D9%8A%D8%A9+%D8%A8%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A\"}, {\"title\": \"\\u062a\\u0645\\u0627\\u0631\\u064a\\u0646 \\u0648\\u0632\\u0646 \\u0627\\u0644\\u062c\\u0633\\u0645 \\u0628\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\", \"description\": \"\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0639\\u0631\\u0636 \\u0642\\u0627\\u0626\\u0645\\u0629 \\u0641\\u064a\\u062f\\u064a\\u0648\\u0647\\u0627\\u062a \\u0639\\u0631\\u0628\\u064a\\u0629 \\u062d\\u0648\\u0644 \\u0647\\u0630\\u0627 \\u0627\\u0644\\u062a\\u0645\\u0631\\u064a\\u0646.\", \"video_id\": null, \"thumbnail\": null, \"channel_title\": \"\\u064a\\u0648\\u062a\\u064a\\u0648\\u0628\", \"video_url\": \"https://www.youtube.com/results?search_query=%D8%AA%D9%85%D8%A7%D8%B1%D9%8A%D9%86+%D9%88%D8%B2%D9%86+%D8%A7%D9%84%D8%AC%D8%B3%D9%85+%D8%A8%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A\"}]','2025-12-02T15:37:19.034799',6),(4,'تمارين القوة','[{\"title\": \"\\u062a\\u0645\\u0627\\u0631\\u064a\\u0646 \\u0627\\u0644\\u0642\\u0648\\u0629 \\u0627\\u0644\\u0645\\u0646\\u0632\\u0644\\u064a\\u0629 \\u0628\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\", \"description\": \"\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0639\\u0631\\u0636 \\u0642\\u0627\\u0626\\u0645\\u0629 \\u0641\\u064a\\u062f\\u064a\\u0648\\u0647\\u0627\\u062a \\u0639\\u0631\\u0628\\u064a\\u0629 \\u062d\\u0648\\u0644 \\u0647\\u0630\\u0627 \\u0627\\u0644\\u062a\\u0645\\u0631\\u064a\\u0646.\", \"video_id\": null, \"thumbnail\": null, \"channel_title\": \"\\u064a\\u0648\\u062a\\u064a\\u0648\\u0628\", \"video_url\": \"https://www.youtube.com/results?search_query=%D8%AA%D9%85%D8%A7%D8%B1%D9%8A%D9%86+%D8%A7%D9%84%D9%82%D9%88%D8%A9+%D8%A7%D9%84%D9%85%D9%86%D8%B2%D9%84%D9%8A%D8%A9+%D8%A8%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A\"}, {\"title\": \"\\u062a\\u0645\\u0627\\u0631\\u064a\\u0646 \\u0648\\u0632\\u0646 \\u0627\\u0644\\u062c\\u0633\\u0645 \\u0628\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\", \"description\": \"\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0639\\u0631\\u0636 \\u0642\\u0627\\u0626\\u0645\\u0629 \\u0641\\u064a\\u062f\\u064a\\u0648\\u0647\\u0627\\u062a \\u0639\\u0631\\u0628\\u064a\\u0629 \\u062d\\u0648\\u0644 \\u0647\\u0630\\u0627 \\u0627\\u0644\\u062a\\u0645\\u0631\\u064a\\u0646.\", \"video_id\": null, \"thumbnail\": null, \"channel_title\": \"\\u064a\\u0648\\u062a\\u064a\\u0648\\u0628\", \"video_url\": \"https://www.youtube.com/results?search_query=%D8%AA%D9%85%D8%A7%D8%B1%D9%8A%D9%86+%D9%88%D8%B2%D9%86+%D8%A7%D9%84%D8%AC%D8%B3%D9%85+%D8%A8%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A\"}]','2025-12-02T16:24:54.838689',6);
/*!40000 ALTER TABLE `sports_data` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-02 18:29:59
