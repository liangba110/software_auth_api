CREATE DATABASE IF NOT EXISTS software_auth DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE software_auth;

-- 用户表
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '登录账号',
    `password` VARCHAR(255) NOT NULL COMMENT '加密密码',
    `status` TINYINT DEFAULT 1 COMMENT '1正常 0封禁',
    `vip_type` TINYINT DEFAULT 0 COMMENT '0普通 1日卡 2月卡 3年卡 4永久',
    `vip_expire_time` DATETIME DEFAULT NULL COMMENT 'VIP过期时间',
    `last_login_time` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_username (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 充值订单表
CREATE TABLE IF NOT EXISTS `recharge_order` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '订单ID',
    `order_sn` VARCHAR(64) NOT NULL UNIQUE COMMENT '订单号',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `pay_type` VARCHAR(20) NOT NULL COMMENT 'alipay/wechat',
    `goods_type` TINYINT NOT NULL COMMENT '1日卡 2月卡 3年卡 4永久',
    `amount` DECIMAL(10,2) NOT NULL COMMENT '支付金额',
    `status` TINYINT DEFAULT 0 COMMENT '0待支付 1已支付 2已过期',
    `transaction_id` VARCHAR(128) DEFAULT NULL COMMENT '第三方交易号',
    `pay_time` DATETIME DEFAULT NULL COMMENT '支付时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_order_sn (`order_sn`),
    INDEX idx_user_id (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='充值订单表';

-- VIP权限变更日志表
CREATE TABLE IF NOT EXISTS `vip_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `order_sn` VARCHAR(64) DEFAULT NULL COMMENT '关联订单号',
    `old_vip_type` TINYINT DEFAULT 0 COMMENT '变更前VIP类型',
    `new_vip_type` TINYINT DEFAULT 0 COMMENT '变更后VIP类型',
    `old_expire_time` DATETIME DEFAULT NULL COMMENT '变更前过期时间',
    `new_expire_time` DATETIME DEFAULT NULL COMMENT '变更后过期时间',
    `operate_type` VARCHAR(50) DEFAULT NULL COMMENT '操作类型',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='VIP变更日志表';
