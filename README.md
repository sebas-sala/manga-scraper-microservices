# Manga Scraper

Manga Scraper is a tool designed to extract information from manga available on a specific website. It retrieves details such as title, categories, images, and more, then sends this data to another service, where it is stored in a database using SQLAlchemy on Supabase.

## Features

- **Data Extraction**: Extracts manga details such as title, categories, images, etc.
- **RabbitMQ Integration**: Uses RabbitMQ to communicate with another service responsible for data storage.
- **Database Storage**: Stores the extracted data in a database using SQLAlchemy and Supabase.
- **Redis for State Management**: Utilizes Redis to store the last scraped page and track if the service has completed or if it’s still in use.

## Requirements

- Python 3.12 or higher
- RabbitMQ (for communication with the database service)
- SQLAlchemy (for interacting with the database)
- Supabase (database storage)
- Redis (for managing scraping state)
