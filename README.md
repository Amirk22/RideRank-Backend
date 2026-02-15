# RideRank

A simple Django project to track and score drivers and passengers based on trips, ratings, and reports.

## Project Scope
RideRank focuses on:
- User management (drivers and passengers)
- Trip management
- Ratings system to score users
- Reporting system for incidents
- Automatic trust score calculation

## Technologies
- Python 3.12
- Django & Django REST Framework
- SQLite
- Docker & Docker Compose

## Installation
1. Clone the repository:
```bash
git clone https://github.com/Amirk22/RideRank-Backend.git
```
```bash
cd RideRank-Backend
```
2. Build and run the project using Docker Compose:
```bash
docker compose up --build
```
3. Access the API:
- Main API: http://localhost:8000/
- Swagger docs: http://localhost:8000/api/swagger
## Initial Data
The project comes with initial users and trips for testing:
- 4 users (2 drivers, 2 passengers)
- 6 trips
- Score events generated automatically

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
