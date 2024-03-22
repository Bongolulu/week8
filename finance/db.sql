CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    username TEXT NOT NULL, 
    hash TEXT NOT NULL, 
    cash NUMERIC NOT NULL DEFAULT 10000.00
);

CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,     
    users_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    datetime DATETIME DEFAULT (DATETIME('now')),
    shares INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    FOREIGN KEY (users_id) REFERENCES users(id)
);

select *,CASE WHEN shares>0 THEN 'BUY' ELSE 'SELL' END AS buysell, shares*price as total from history wher users_id=?
