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
-- Table structure for table `medication_reminders`
--

DROP TABLE IF EXISTS `medication_reminders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medication_reminders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `medication_id` int NOT NULL,
  `reminder_time` time NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `medication_id` (`medication_id`),
  CONSTRAINT `medication_reminders_ibfk_1` FOREIGN KEY (`medication_id`) REFERENCES `medications` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medication_reminders`
--

LOCK TABLES `medication_reminders` WRITE;
/*!40000 ALTER TABLE `medication_reminders` DISABLE KEYS */;
INSERT INTO `medication_reminders` VALUES (19,12,'03:43:00','2025-11-30 00:21:32','2025-11-30 00:21:32'),(20,12,'03:43:00','2025-11-30 00:21:32','2025-11-30 00:21:32'),(21,13,'02:45:00','2025-11-30 00:21:32','2025-11-30 00:21:32'),(22,14,'08:50:00','2025-11-30 00:21:32','2025-11-30 00:21:32'),(23,14,'07:50:00','2025-11-30 00:21:32','2025-11-30 00:21:32'),(24,16,'04:19:00','2025-11-30 00:22:34','2025-11-29 22:22:35'),(25,16,'06:19:00','2025-11-30 00:22:34','2025-11-29 22:22:35'),(26,17,'00:25:00','2025-11-30 00:22:53','2025-11-29 22:22:53'),(27,18,'18:59:00','2025-11-30 18:55:11','2025-11-30 16:55:11'),(28,19,'17:42:00','2025-12-02 17:38:44','2025-12-02 15:38:45'),(29,20,'18:28:00','2025-12-02 18:24:10','2025-12-02 16:24:11');
/*!40000 ALTER TABLE `medication_reminders` ENABLE KEYS */;
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
