sudo docker login
sudo docker pull ruzzik/foodgram:latest
sudo docker pull ruzzik/foodgram-react:latest
sudo docker compose up --build -d
sudo docker exec -it ruzzik-backend-1 python manage.py migrate
sudo docker exec -it ruzzik-backend-1 python manage.py load-ingredients
sudo docker exec -it ruzzik-backend-1 python manage.py collectstatic
