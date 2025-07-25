# NBA Arbitrage Project (Monorepo)

## Directory Structure
```
project-root/
├── docker-compose.yml
├── odds_fetcher/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── arb_engine/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py  # FastAPI main app
│   ├── ...     # (other backend modules)
└── frontend/ (optional)
    ├── Dockerfile
    ├── package.json
    └── src/
```

## Service Descriptions
- **backend/**: Main FastAPI app, DB models, arbitrage logic, and scheduler.
- **odds_fetcher/**: (Placeholder) For a future microservice to fetch odds.
- **arb_engine/**: (Placeholder) For a future microservice to compute arbitrage.
- **frontend/**: (Optional) For a web UI.

## Placeholders & TODOs
- All `main.py` files in `odds_fetcher/` and `arb_engine/` are placeholders. Add your logic as needed.
- All `requirements.txt` files in those folders are currently copies; update as needed for each service.
- The `frontend/` folder is a placeholder for a Node.js app. Add your own `package.json` and code.
- The `.env` file (not included) must be created in the project root or in each service as needed. See previous instructions for required variables.

## Running the Project
1. **Fill in all placeholders and .env values as needed.**
2. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```
3. **Initialize the backend database:**
   ```bash
   docker-compose exec backend python
   >>> from models import Base
   >>> from db import engine
   >>> Base.metadata.create_all(bind=engine)
   >>> exit()
   ```
4. **Access the backend API:** [http://localhost:8000/arbs](http://localhost:8000/arbs)

## Customizing
- Add your own logic to `odds_fetcher/` and `arb_engine/` as your architecture evolves.
- Update Dockerfiles and requirements as needed for each service. 