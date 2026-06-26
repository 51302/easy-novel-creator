-- ============================================
-- Auth System - 数据库初始化脚本
-- 使用方式: mysql -u root -p < init_db.sql
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `auth_system`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE `auth_system`;

-- 创建用户表
CREATE TABLE IF NOT EXISTS `users` (
    `id`         INT AUTO_INCREMENT PRIMARY KEY       COMMENT '用户ID',
    `username`   VARCHAR(50)  NOT NULL                COMMENT '用户名',
    `password`   VARCHAR(255) NOT NULL                COMMENT '密码（bcrypt加密）',
    `token`      VARCHAR(500) DEFAULT NULL            COMMENT '当前JWT Token',
    `status`     SMALLINT     NOT NULL DEFAULT 1      COMMENT '状态: 0=禁用, 1=正常',
    `email`      VARCHAR(100) DEFAULT NULL            COMMENT '邮箱',
    `phone`      VARCHAR(20)  DEFAULT NULL            COMMENT '手机号',
    `superuser`  SMALLINT     NOT NULL DEFAULT 0      COMMENT '超级管理员: 0=否, 1=是',
    `created_at` DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE KEY `uk_username` (`username`),
    INDEX       `idx_status`  (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 创建作品表 (novels)
CREATE TABLE IF NOT EXISTS `novels` (
    `id`           INT AUTO_INCREMENT PRIMARY KEY       COMMENT '作品自增ID',
    `novel_uuid`   VARCHAR(36)  NOT NULL                COMMENT '作品唯一UUID',
    `author_id`    INT          NOT NULL                COMMENT '作者用户ID',
    `author_name`  VARCHAR(50)  NOT NULL                COMMENT '作者用户名',
    `title`        VARCHAR(100) NOT NULL                COMMENT '书名/作品名称',
    `novel_type`   VARCHAR(50)  DEFAULT NULL            COMMENT '作品类型/目标读者',
    `tags`         TEXT         DEFAULT NULL            COMMENT '标签 (JSON字符串)',
    `likes`        BIGINT       NOT NULL DEFAULT 0      COMMENT '点赞量',
    `views`        BIGINT       NOT NULL DEFAULT 0      COMMENT '观看量/阅读量',
    `comments`     BIGINT       NOT NULL DEFAULT 0      COMMENT '评论量',
    `created_at`   DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`   DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE KEY `uk_novel_uuid` (`novel_uuid`),
    INDEX       `idx_author_id` (`author_id`),
    INDEX       `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作品表';

-- 插入一个默认管理员用户（密码: admin123，bcrypt加密）
-- 生产环境请务必修改密码！
INSERT INTO `users` (`username`, `password`, `status`, `email`, `superuser`)
VALUES (
    'admin',
    '$2b$12$LJ3m4ys3Lk0TSwHCpNqrBeKCwvGPJqWM0wGcFPhBmSgFCsOzGNqcK',
    1,
    'admin@example.com',
    1
);
