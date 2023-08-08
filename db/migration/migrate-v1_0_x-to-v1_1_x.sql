CREATE TABLE if not exists menu (
  id SERIAL PRIMARY KEY,
  menu_date DATE UNIQUE DEFAULT CURRENT_DATE,
  menu jsonb[]
);

ALTER TABLE users ADD COLUMN ui_theme text DEFAULT 'light';
ALTER TABLE users ADD COLUMN ui_color text DEFAULT 'falusi';
