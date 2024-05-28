#!/bin/bash

# Запустить Docker Compose
docker-compose up --build &

# Дождаться запуска контейнера
sleep 10

# Открыть браузер по адресу http://localhost:5001
xdg-open http://http://127.0.0.1:5001/ || open http://127.0.0.1:5001/ || start http://127.0.0.1:5001/
