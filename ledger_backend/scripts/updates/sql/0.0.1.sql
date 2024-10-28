CREATE TABLE user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    urn VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    is_logged_in BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    last_login DATETIME,
    updated_at DATETIME,
    INDEX idx_user_urn (urn),
    INDEX idx_user_email (email),
    INDEX idx_user_created_at (created_at)
);