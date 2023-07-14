CREATE TYPE order_state_type AS ENUM ('collect', 'order', 'closed');
CREATE TYPE subscribe_type AS ENUM ('none', 'temp', 'full');
CREATE TYPE daily_state_type AS ENUM ('none', 'video', 'skip', 'done');

CREATE TABLE if not exists orders (
  id SERIAL PRIMARY KEY,
  order_date DATE UNIQUE DEFAULT CURRENT_DATE,
  order_state order_state_type DEFAULT 'collect',
  basket jsonb
);

CREATE TABLE if not exists menu (
  id SERIAL PRIMARY KEY,
  menu_date DATE UNIQUE DEFAULT CURRENT_DATE,
  menu jsonb
);

CREATE TABLE if not exists users (
  id SERIAL PRIMARY KEY,
  username text UNIQUE NOT NULL,
  subscribed subscribe_type NOT NULL DEFAULT 'none',
  daily_state daily_state_type NOT NULL DEFAULT 'none'
);
