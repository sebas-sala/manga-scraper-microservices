from app import engine
from app.models import Base
from app.consumer import Consumer
import app.logging_config 

def start_consumers():
    """Start all consumers"""
    with Consumer() as consumer:
        consumer.start_consumers()

def main():
    """Main function"""
    Base.metadata.create_all(bind=engine)
    start_consumers()

if __name__ == "__main__":
    main()