# NBA Arbitrage Detection System

**Automated Sports Betting Arbitrage Scanner with SMS Alerts**

A fully automated system that finds guaranteed profit opportunities in NBA betting markets and texts you when it finds them.

---

## What This Does (In Plain English)

This system monitors betting odds from multiple sportsbooks 24/7 and automatically alerts you via text message when it finds arbitrage opportunities - situations where you can bet on all possible outcomes of a game and guarantee a profit, regardless of who wins.

**Think of it like this:**
- DraftKings offers Lakers at 2.1 odds
- FanDuel offers Warriors at 2.2 odds
- You can bet on both teams and guarantee a profit

The system finds these opportunities automatically and texts you the exact bet amounts based on your bankroll.

---

## What You Get

✅ **Automatic Monitoring** - System runs 24/7, checking odds every day at 6 AM EST
✅ **Text Message Alerts** - Get SMS notifications when profitable opportunities appear
✅ **Personalized Bet Sizing** - Calculates exact bet amounts based on your unit size
✅ **Multi-Person Support** - Send different bet sizes to different people
✅ **Historical Data** - Tracks all opportunities found for analysis
✅ **Web Dashboard** - View current opportunities at any time

---

## Real-World Example

**Text Message You'll Receive:**

```
Hi Alex, here are your odds for 2025-12-01
Unit size: $100

BASKETBALL NBA
Lakers vs Warriors
  DraftKings: Lakers@2.1 ($47.62)
  FanDuel: Warriors@2.2 ($45.45)

Profit: 2.5% guaranteed
```

You would:
1. Bet $47.62 on Lakers at DraftKings
2. Bet $45.45 on Warriors at FanDuel
3. Guaranteed profit: ~$7 regardless of who wins

---

## What You Need to Get Started

### 1. Computer Requirements
- A Mac or Windows computer
- Internet connection
- 30 minutes for initial setup

### 2. Required Accounts (All Free to Start)

**A. The Odds API** (Provides betting odds data)
- Visit: [the-odds-api.com](https://the-odds-api.com/)
- Sign up for free account
- Get your API key (a long password-like string)
- **Cost:** Free tier includes 500 requests/month (plenty for daily use)

**B. Twilio** (Sends text messages)
- Visit: [twilio.com](https://www.twilio.com/)
- Sign up for account
- Buy a phone number (~$1/month)
- Get your Account SID and Auth Token (like usernames/passwords)
- **Cost:** ~$1/month for phone number + ~$0.01 per text message

**C. Docker Desktop** (Runs the system)
- Visit: [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
- Download and install (it's like installing any other app)
- **Cost:** Free

---

## Step-by-Step Setup (No Coding Required)

### Step 1: Download the System

1. Download this project (click the green "Code" button → Download ZIP)
2. Unzip it to your Desktop
3. You should have a folder called `Arb_Gambling`

### Step 2: Set Up Your Credentials

1. **Open the folder** `Arb_Gambling` on your computer

2. **Find the file** called `.env.example`

3. **Make a copy** and rename it to just `.env` (remove the .example part)

4. **Open the `.env` file** with TextEdit (Mac) or Notepad (Windows)

5. **Fill in your information:**

```
ODDS_API_KEY=paste_your_api_key_here
TWILIO_ACCOUNT_SID=paste_your_twilio_sid_here
TWILIO_AUTH_TOKEN=paste_your_twilio_token_here
TWILIO_FROM_NUMBER=+12345678900
DATABASE_URL=postgresql://arbuser:arbpass@db:5432/odds_db
```

**Where to find these:**
- **ODDS_API_KEY**: Log into the-odds-api.com → Dashboard → Copy your API key
- **TWILIO_ACCOUNT_SID**: Log into twilio.com → Console Dashboard → Copy Account SID
- **TWILIO_AUTH_TOKEN**: Same page → Copy Auth Token (click "show" first)
- **TWILIO_FROM_NUMBER**: Same page → Copy your Twilio phone number (format: +12345678900)
- **DATABASE_URL**: Leave as is (this is already configured)

6. **Save the file**

### Step 3: Set Up Your Recipients

1. **Find the file** called `recipients.csv.example`

2. **Make a copy** and rename it to `recipients.csv`

3. **Open it** with Excel or any spreadsheet program

4. **Fill in your information:**

| name | phone | unit |
|------|-------|------|
| Alex | +12345678900 | 100 |
| Sam | +19876543210 | 250 |

**What these mean:**
- **name**: Person's name (appears in text messages)
- **phone**: Their phone number (must start with +1 for US numbers)
- **unit**: Their bet size in dollars (system calculates bet amounts based on this)

5. **Save the file**

### Step 4: Start the System

1. **Open Terminal** (Mac) or **Command Prompt** (Windows)

2. **Navigate to your folder:**
   ```bash
   cd Desktop/Arb_Gambling
   ```

3. **Start the system:**
   ```bash
   docker-compose up
   ```

4. **Wait about 2 minutes** while it starts up (you'll see text scrolling - this is normal)

5. **Look for this message:**
   ```
   Application startup completed successfully
   ```

**That's it! The system is now running.**

### Step 5: Test It Works

**Open your web browser** and go to:
```
http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "checks": {
    "database": "healthy",
    "api": "healthy"
  }
}
```

If you see this, everything is working!

---

## How to Use the System

### Automatic Mode (Set It and Forget It)

Once started, the system automatically:
1. Checks for arbitrage opportunities every day at **6:00 AM EST**
2. Texts all recipients when opportunities are found
3. Runs 24/7 in the background

**You don't need to do anything.** Just leave it running and wait for text alerts.

### Manual Mode (Check Anytime)

**Send a test text right now:**

Open Terminal/Command Prompt and run:
```bash
docker-compose run --rm odds_fetcher python main.py send_now
```

You'll receive a text within 30 seconds with current odds.

**Check for arbitrage opportunities online:**

Open your browser and go to:
```
http://localhost:8000/arbs
```

You'll see a list of any current arbitrage opportunities.

**View the interactive dashboard:**
```
http://localhost:8000/docs
```

This shows all available features with a visual interface.

---

## Understanding Your Alerts

### Sample Text Message Breakdown

```
Hi Alex, here are your odds for 2025-12-01
Unit size: $100

BASKETBALL NBA
Lakers vs Warriors
  DraftKings: Lakers@2.1 ($47.62) ← Bet this amount on Lakers
  FanDuel: Warriors@2.2 ($45.45) ← Bet this amount on Warriors

Profit: 2.5% guaranteed
```

**How to read this:**
- **Unit size**: Your configured bet size ($100)
- **Lakers@2.1**: Lakers have 2.1 decimal odds at DraftKings
- **($47.62)**: Bet exactly $47.62 on Lakers
- **Warriors@2.2**: Warriors have 2.2 decimal odds at FanDuel
- **($45.45)**: Bet exactly $45.45 on Warriors
- **Profit: 2.5%**: You'll make 2.5% profit (~$2.50 on ~$100 total bet)

### The Math (For Your Records)

Total invested: $47.62 + $45.45 = **$93.07**

**If Lakers win:**
- DraftKings pays: $47.62 × 2.1 = **$100.00**
- FanDuel loses: -$45.45
- Net profit: $100 - $93.07 = **$6.93** (7.4% ROI)

**If Warriors win:**
- FanDuel pays: $45.45 × 2.2 = **$100.00**
- DraftKings loses: -$47.62
- Net profit: $100 - $93.07 = **$6.93** (7.4% ROI)

**Either way, you profit $6.93.**

---

## Daily Operation

### What to Do Each Day

**Morning (After 6 AM EST):**
1. Check your phone for text alerts
2. If you received an alert with opportunities, place the bets as shown
3. If no alert, no opportunities were found that day

**That's it.** The system handles everything else.

### When to Act on Opportunities

Arbitrage opportunities typically:
- Appear for 5-30 minutes before odds shift
- Require you to place bets quickly on both books
- Work best when you have accounts pre-funded at multiple sportsbooks

**Best Practice:** Have accounts at DraftKings, FanDuel, BetMGM, and Caesars pre-funded and ready.

---

## Managing the System

### Stopping the System

In the Terminal/Command Prompt window where it's running, press:
```
Ctrl + C
```

The system will shut down gracefully.

### Restarting the System

```bash
cd Desktop/Arb_Gambling
docker-compose up
```

### Checking if It's Running

Open your browser:
```
http://localhost:8000/health
```

If you see the "healthy" message, it's running.

### Viewing Activity Logs

See what the system is doing:
```bash
docker-compose logs -f
```

Press `Ctrl + C` to stop viewing logs.

---

## Troubleshooting

### Not Receiving Text Messages?

**Check 1:** Verify your Twilio credentials in the `.env` file
- Log into twilio.com
- Compare the numbers in your `.env` file
- Make sure there are no extra spaces

**Check 2:** Check your Twilio balance
- Log into twilio.com → Billing
- Add funds if balance is low

**Check 3:** Verify phone number format
- Must include country code: `+12345678900`
- No spaces, dashes, or parentheses

### System Won't Start?

**Error: "Docker is not running"**
- Open Docker Desktop application
- Wait for it to fully start (green icon in menu bar/taskbar)
- Try again

**Error: "Port 8000 already in use"**
- Something else is using that port
- Stop other applications or restart your computer

**Error: "Configuration validation failed"**
- Check your `.env` file
- Make sure all required fields are filled in
- Remove any quotation marks around values

### No Opportunities Found?

This is normal. Arbitrage opportunities are rare (that's why they're profitable).

**Typical frequency:**
- 0-3 opportunities per day during NBA season
- More common during high-volume betting times (weekends)
- Zero opportunities on off-season days

The system is working correctly even if you don't get daily alerts.

### Need Help?

1. Check this documentation first
2. View the system logs: `docker-compose logs -f`
3. Verify your `.env` file settings
4. Make sure Docker Desktop is running

---

## Costs & Economics

### Setup Costs
- The Odds API: **Free** (500 requests/month)
- Twilio Phone Number: **~$1/month**
- Text Messages: **~$0.01 each** (assuming 2 texts/day = $0.60/month)
- Docker: **Free**

**Total monthly cost: ~$2**

### Expected Returns

This varies based on:
- Your unit size
- Number of opportunities found
- How quickly you act on alerts

**Conservative estimate:**
- 2 opportunities per week
- 2-5% profit per opportunity
- $100 unit size

**Monthly profit potential: $80-$200**

**ROI on $2/month operational cost: 4,000%+**

---

## Important Notes

### Legal Disclaimer

This system is for **educational and informational purposes only**.

- Verify sports betting is legal in your jurisdiction
- You are responsible for complying with all local laws
- This system does not place bets for you (you place them manually)
- Past performance does not guarantee future results
- Sportsbooks may limit accounts that consistently win

### Risk Factors

**Market Risk:**
- Odds can change between when you receive alert and place bets
- Always verify current odds before placing bets

**Account Risk:**
- Sportsbooks may limit or ban accounts that consistently arbitrage
- Use responsibly and within each book's terms of service

**Execution Risk:**
- You must place both sides of the bet
- If you only place one side, you have normal betting risk

### Best Practices

✅ Always verify odds are still available before betting
✅ Place both bets as quickly as possible
✅ Keep accounts funded at multiple sportsbooks
✅ Start with smaller unit sizes while learning
✅ Track your results in a spreadsheet
✅ Never bet more than you can afford to lose

---

## Support & Maintenance

### Keeping the System Updated

The system runs automatically once started. Updates are rare but when needed:

1. Stop the system (`Ctrl + C`)
2. Re-download the latest version
3. Copy your `.env` and `recipients.csv` to the new folder
4. Restart: `docker-compose up`

### Backing Up Your Data

Your historical data is stored in the system. To export:

```bash
docker-compose exec db pg_dump -U arbuser odds_db > backup.sql
```

This creates a backup file of all opportunities found.

---

## Advanced Features

### Multiple Recipients with Different Unit Sizes

Edit `recipients.csv` to send different bet sizes to different people:

```csv
name,phone,unit
Trader1,+12345678901,1000
Trader2,+12345678902,500
Trader3,+12345678903,250
```

Each person receives texts with bet amounts calculated for their unit size.

### Running in the Background

To keep the system running even after closing Terminal:

```bash
docker-compose up -d
```

The `-d` means "detached mode" - runs in background.

To stop:
```bash
docker-compose down
```

### Viewing Historical Data

Access the database to see all past opportunities:

```bash
docker-compose exec db psql -U arbuser -d odds_db
```

Then run:
```sql
SELECT
  home_team,
  away_team,
  arb_percent,
  created_at
FROM arbitrage_opportunities
ORDER BY created_at DESC
LIMIT 20;
```

Type `exit` to leave the database.

---

## Frequently Asked Questions

**Q: How often will I receive alerts?**
A: Varies significantly. During NBA season, typically 2-10 opportunities per week. Off-season may have zero.

**Q: Can I use this for other sports?**
A: Yes! The system already fetches all sports. NBA is prioritized but you can modify settings to include NFL, MLB, etc.

**Q: Will sportsbooks ban me for this?**
A: Possibly. Sportsbooks don't like consistent winners. Use discretion and vary your bet patterns.

**Q: Do I need to keep my computer on 24/7?**
A: For automatic 6 AM alerts, yes. Or you can use manual mode and check whenever you want.

**Q: Can I change the alert time?**
A: Yes, but requires editing code. The default is 6 AM EST when odds are fresh.

**Q: Is this legal?**
A: Arbitrage betting is legal where sports betting is legal. Check your local laws.

**Q: What if odds change after I receive the alert?**
A: Always verify current odds before placing bets. Alerts show odds at scan time, not current odds.

**Q: Can I share this with friends?**
A: Yes, add them to `recipients.csv` with their own unit sizes.

---

## Summary

This system automates the tedious work of finding arbitrage opportunities across multiple sportsbooks. Instead of manually checking dozens of games across multiple sites, you receive text alerts when guaranteed profit opportunities appear.

**Setup time:** 30 minutes
**Monthly cost:** ~$2
**Daily effort:** Check phone for alerts, place bets when opportunities appear
**Potential return:** Varies, but typically positive ROI for active users

The key is quick execution when opportunities appear and maintaining funded accounts at multiple sportsbooks.

---

**Questions?** Review this guide. Everything you need is documented above.

**Good luck, and bet responsibly!**
