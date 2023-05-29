CREATE TYPE order_state AS ENUM ('collect', 'order', 'closed');
CREATE TABLE if not exists orders (
  id SERIAL PRIMARY KEY,
  order_date DATE DEFAULT CURRENT_DATE,
  order_state order_state DEFAULT 'collect',
  basket jsonb
);
