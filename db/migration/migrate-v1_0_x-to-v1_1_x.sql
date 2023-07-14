CREATE TABLE if not exists menu (
  id SERIAL PRIMARY KEY,
  menu_date DATE UNIQUE DEFAULT CURRENT_DATE,
  menu jsonb[]
);
