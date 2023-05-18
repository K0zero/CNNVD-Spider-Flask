/*
 Navicat Premium Data Transfer

 Source Server         : 星际159.75.50.79
 Source Server Type    : MySQL
 Source Server Version : 50734
 Source Host           : 159.75.50.79:3306
 Source Schema         : vul

 Target Server Type    : MySQL
 Target Server Version : 50734
 File Encoding         : 65001

 Date: 14/05/2023 03:51:17
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `phone` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `addTime` datetime(0) NULL DEFAULT NULL,
  `admin` int(11) NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, 'admin', '18888888888', '123456', '2023-05-13 23:42:35', 1);
INSERT INTO `user` VALUES (8, 'test', '18620127807', '123456', '2023-05-13 21:00:52', 1);
INSERT INTO `user` VALUES (9, 'test2', '18620128888', '123456', '2023-05-14 00:12:30', 0);

SET FOREIGN_KEY_CHECKS = 1;
