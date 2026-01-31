# 🔑 API Keys Setup Guide

This guide will help you get **FREE** API keys for real gaming data.

## 🎯 Quick Start

Run the interactive setup script:
```bash
python setup_api_keys.py
```

This will guide you through setting up all API keys interactively.

---

## 📋 API Keys Overview

### ✅ OpenDota API (Dota 2) - **NO KEY NEEDED!**
- **Status**: ✅ Already working - No API key required!
- **URL**: https://www.opendota.com/
- **Rate Limit**: 60 requests/minute
- **What it provides**: Real Dota 2 match data, hero stats, player rankings
- **Setup**: None needed - it's already fetching real data!

### 🔑 Steam Web API
- **Status**: Optional (for CS:GO, GTA 5, Dota 2 Steam data)
- **Cost**: FREE
- **URL**: https://steamcommunity.com/dev/apikey
- **Rate Limit**: 100,000 requests/day
- **What it provides**: Player stats, game info, recent games
- **Setup Steps**:
  1. Go to https://steamcommunity.com/dev/apikey
  2. Log in with your Steam account
  3. Enter a domain name (can be anything, e.g., "localhost")
  4. Click "Register"
  5. Copy your API key
  6. Run `python setup_api_keys.py` and paste it when prompted

### 🔑 Riot Games API (Valorant)
- **Status**: Optional (for Valorant data)
- **Cost**: FREE
- **URL**: https://developer.riotgames.com/
- **Rate Limit**: 
  - Development: 100 requests/2 minutes
  - Production: 500 requests/10 minutes (requires approval)
- **What it provides**: Match data, player stats, rank information
- **Setup Steps**:
  1. Go to https://developer.riotgames.com/
  2. Sign up for a free account
  3. Create a new application
  4. Copy your API key
  5. Run `python setup_api_keys.py` and paste it when prompted
  6. **Note**: API key expires after 24 hours (free tier). You'll need to regenerate it.

---

## 🔧 Manual Setup

If you prefer to set up API keys manually:

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```env
   STEAM_API_KEY=your_steam_api_key_here
   RIOT_API_KEY=your_riot_api_key_here
   ```

3. **IMPORTANT**: The `.env` file is automatically ignored by git and will NOT be committed to the repository.

4. The pipeline will automatically read from `.env` file.

---

## ✅ Verification

After setting up API keys, verify they work:

1. Run the dashboard:
   ```bash
   python -m streamlit run dashboard/app.py
   ```

2. Check the sidebar - you should see API status indicators:
   - ✅ Green = API configured and working
   - ⚠️ Yellow = API key not configured (optional)
   - ❌ Red = API error

---

## 📝 Notes

- **OpenDota**: No key needed, works immediately
- **Steam API**: Free, unlimited requests (within rate limits)
- **Riot API**: Free but keys expire after 24 hours (development tier)
- All API keys are stored in `.env` file (not committed to git)
- The pipeline works without API keys (uses OpenDota for Dota 2 data)

---

## 🆘 Troubleshooting

**Problem**: API key not working
- **Solution**: Check that the key is correctly set in `.env` file
- **Solution**: Verify the key hasn't expired (Riot keys expire after 24 hours)

**Problem**: Rate limit errors
- **Solution**: The pipeline includes rate limiting. Wait a few minutes and try again.

**Problem**: No data showing
- **Solution**: Run the ETL pipeline first: `python src/etl/run_pipeline.py`
- **Solution**: Check API status in the dashboard sidebar
