ALTER TABLE orders ADD CONSTRAINT unique_order_date UNIQUE (order_date);

CREATE TYPE subscribe_type AS ENUM ('none', 'temp', 'full');
CREATE TYPE daily_state_type AS ENUM ('none', 'video', 'skip', 'done');

CREATE TABLE if not exists users (
  id SERIAL PRIMARY KEY,
  username text UNIQUE NOT NULL,
  subscribed subscribe_type NOT NULL DEFAULT 'none',
  daily_state daily_state_type NOT NULL DEFAULT 'none'
);
