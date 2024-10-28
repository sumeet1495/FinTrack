CREATE TABLE account (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    urn TEXT NOT NULL,
    user_id BIGINT,
    name TEXT NOT NULL,
    currency_id BIGINT,
    balance FLOAT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_on DATETIME,
    created_by BIGINT,
    updated_on DATETIME,
    updated_by BIGINT,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (currency_id) REFERENCES currency_lk(id),
    FOREIGN KEY (created_by) REFERENCES user(id)
);

CREATE TABLE currency_lk (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    code TEXT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    created_on DATETIME,
    updated_on DATETIME
);

CREATE TABLE transaction (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    urn TEXT,
    payer_account_id BIGINT,
    payer_account_urn TEXT,
    payee_account_id BIGINT,
    payee_account_urn TEXT,
    amount FLOAT,
    purpose TEXT,
    created_on DATETIME,
    created_by BIGINT,
    updated_on DATETIME,
    updated_by BIGINT,
    FOREIGN KEY (payer_account_id) REFERENCES account(id),
    FOREIGN KEY (payee_account_id) REFERENCES account(id),
    FOREIGN KEY (created_by) REFERENCES user(id)
);

CREATE TABLE balances (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    account_id BIGINT,
    account_urn TEXT NOT NULL,
    total_balance FLOAT,
    total_credit_balance FLOAT,
    total_debit_balance FLOAT,
    created_on DATETIME,
    created_by BIGINT,
    updated_on DATETIME,
    updated_by BIGINT,
    FOREIGN KEY (account_id) REFERENCES account(id),
    FOREIGN KEY (created_by) REFERENCES user(id)
);