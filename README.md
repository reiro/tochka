Installation
# tickers.txt - названия акций
python3 -v 3.6.3
django -v 2.1.dev20180316013315
pip3 install multiprocessing
pip3 install beautifulsoup4
pip3 install psycopg2


Миграция:
./manage.py migrate shares

Парсер:
python3 parser.py N, N - threads count

server:
python3 manage.py runserver