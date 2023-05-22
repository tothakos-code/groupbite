CREATE TABLE if not exists orders (
  id SERIAL PRIMARY KEY,
  order_date DATE DEFAULT CURRENT_DATE,
  basket jsonb
);
