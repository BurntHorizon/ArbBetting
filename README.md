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
- **odds_fetcher/**: Fetches odds and sends SMS to recipients.
- **arb_engine/**: (Placeholder) For a future microservice to compute arbitrage.
- **frontend/**: (Optional) For a web UI.

---

## Setup Instructions

### 1. Create Your `.env` File
Create a file named `.env` in your project root with the following contents:
```
ODDS_API_KEY=your_odds_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_FROM_NUMBER=+1234567890  # Replace with your Twilio phone number
DATABASE_URL=postgresql://arbuser:arbpass@db:5432/odds_db
NY_BOOKIES=draftkings,fanduel,betmgm,caesars,pointsbet,wynnbet,bet365,barstool
RECIPIENTS_CSV=recipients.csv
```
- Replace the values with your real API keys and phone number.
- **Never commit your real `.env` to GitHub!**

### 2. Create Your `recipients.csv` File
Create a file named `recipients.csv` in your project root (or as specified in `.env`). Example:
```
name,phone,unit
Alex,+12345550123,10
Sam,+12345550124,25
Jamie,+12345550125,50
```
- Add as many rows as you want.
- `unit` is the bet size for each recipient.
- Phone numbers should be in E.164 format (e.g., +12345550123).

### 3. Add a `.gitignore` File
Create a `.gitignore` in your project root with at least these lines:
```
.env
recipients.csv
odds_fetcher/recipients.csv
__pycache__/
*.pyc
venv/
node_modules/
.DS_Store
```
- This keeps secrets and private data out of git.

### 4. Initialize Git and Push to GitHub
If you haven’t already:
```bash
git init
git add .gitignore
# Add all files and commit
git add .
git commit -m "Initial commit"
# Add your GitHub repo as remote
git remote add origin https://github.com/your-username/your-repo.git
# Check your branch name (main or master)
git branch
# Push using the correct branch name (usually main):
git push -u origin main
```
If you see an error about `master` not matching, use `main` or your current branch name.

---

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
5. **Test SMS sending immediately:**
   ```bash
   docker-compose run --rm odds_fetcher python main.py send_now
   ```

---

## Best Practices
- **Never commit `.env` or `recipients.csv` to git.**
- Use strong, unique API keys and tokens.
- Use a local Twilio number for easiest SMS setup (toll-free requires verification).
- Keep your dependencies up to date.

---

## Customizing
- Add your own logic to `odds_fetcher/` and `arb_engine/` as your architecture evolves.
- Update Dockerfiles and requirements as needed for each service. 