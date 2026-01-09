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
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(80) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `last_name` varchar(80) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `diet_history` text COLLATE utf8mb4_general_ci,
  `usage_dates` text COLLATE utf8mb4_general_ci,
  `consultation_history` text COLLATE utf8mb4_general_ci,
  `challenges_completed` int DEFAULT '0',
  `consultations` int DEFAULT '0',
  `telegram_chat_id` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Rawan','Magdy','rawan@example.com','01000000000','scrypt:32768:8:1$a7iXBT7X2iwhUx6T$a6ce2b3276b83d547eea400604c9669459beb4ebb3c00064034481a084bc4b9edb03828815b61d77f481ccefaa05d772876d80f9b6c354fbdca89213e31a178e',NULL,NULL,NULL,NULL,0,0,NULL,NULL),(2,'وفاء','عاطف','wafaa@gmail.com','111','scrypt:32768:8:1$aMpKwGJAlNT6ezGs$a5afe4a3b87ce6fe56367169cfe62e2c08f283cf19d9e1be948f5955c290821009331e24b3feea2d0ddc405b52e81c48baa91678c379efcbc692da91eede4f15',NULL,NULL,'[\"2025-11-14\"]',NULL,0,0,NULL,NULL),(3,'محمد','مجدي','mohamad@gmi.com','1234567','scrypt:32768:8:1$Eoc7wMpeZ2rUhNzu$adb1feab8a49adb697dd777ad04eb4f2a97ef869e63a33d793251b0699efc72959b3491c5cbb5a8d52f61228153059aef5f5cb3066f81f35f553f403c27deb65','2025-11-14 23:10:30',NULL,'[\"2025-11-14\", \"2025-11-15\"]','[\"2025-11-14T23:15:59.224285\"]',0,1,'123456789',NULL),(4,'Mohamed','Asem','asemm5303@gmail.com','01018211571','scrypt:32768:8:1$QdRujlHk9oY03ZnL$7ae9ab7738a77369a20148a7d955febdc694a24edc4dada4ca7174ec74933c4bfb07721ee86f7f278efc1bb7bd7ded3ca9c978c43fba87fb5455991a9283055a','2025-11-15 07:48:35',NULL,'[\"2025-11-15\"]',NULL,0,0,NULL,NULL),(5,'روانن','محمد','dsmcjsmc@hejklf','0987654','scrypt:32768:8:1$n5G7RbQUacD2fmYm$887979fc9371d72d8ddc964d491d34d31ad8835e275f425a58a9502d6787b7d82f2327077ff8a16f6ebcc53fa7f4404ed8b0425844edcbaa287cd5217010e15e','2025-11-29 15:50:44',NULL,'[\"2025-11-29\"]',NULL,0,0,NULL,'2025-11-29 15:50:59'),(6,'rawan','مجدي','gdxbb00@gmail.com','01024690050','scrypt:32768:8:1$LWMcu6HvlQCKq1nl$939f1732b290b1ae2dc520f5ce72553d8d0463954cc84909b88b1a28f97beca650215122a31a7ab16c5df4dd61bf1bd6aaf44f567daf7b5169b5c6175ab33b83','2025-11-29 22:18:43',NULL,'[\"2025-11-29\", \"2025-12-02\"]','[\"2025-11-29T22:19:06.038400\", \"2025-12-02T15:28:43.167357\", \"2025-12-02T15:38:18.725480\", \"2025-12-02T16:23:45.506386\"]',1,4,'123458909965','2025-12-02 16:23:46'),(7,'wxshjhjxdsxh','hdxsbh','xhjds@gmail.com','012354674387','scrypt:32768:8:1$m9W5fJPgRK0jK5wX$1eb1a8c8e4c54482497db1f94ae6b06209110fb436f01b96d8ed3004a19ceb3a1e6834560e57f8fbe516747cf4e68a110948806d5afd475df852d03aab743bf5','2025-11-30 16:50:47',NULL,'[\"2025-11-30\"]','[\"2025-11-30T16:53:48.761548\"]',1,1,'123458909965','2025-11-30 16:57:28');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-02 18:29:58
