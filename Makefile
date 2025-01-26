db:
	docker-compose down && docker-compose up db-service

scraper:
	docker-compose down && docker-compose up scraping-service

dev:
	docker-compose down && docker-compose up -d

down: 
	docker-compose down

build:
	docker-compose down && docker-compose build

start:
	docker-compose down && docker-compose up

test:
	docker-compose down && docker-compose -f docker-compose.test.yml up -d