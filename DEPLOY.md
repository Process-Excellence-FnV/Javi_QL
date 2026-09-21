# Deployment Guide - Javi.QL

Deploy Javi.QL to the cloud in minutes with zero installation for teammates!

## Quick Deployment (Render.com - FREE)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Authorize your GitHub account

### Step 2: Deploy the App
1. On Render dashboard, click **"New +"** → **"Web Service"**
2. Select **"Deploy from GitHub"**
3. Find and select: `janhavichauhanint-art/Javi_QL`
4. Fill in the form:
   - **Name**: `javiql` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Scroll down to **"Environment"** section
6. Add these variables:
   ```
   DB_TYPE=postgresql
   DB_HOST=your-database-host.com
   DB_PORT=5432
   DB_NAME=your_database
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```
7. Click **"Create Web Service"**

### Step 3: Wait for Build
- Render builds and deploys (3-5 minutes)
- You get a URL like: `https://javiql.onrender.com`
- ✅ Done!

### Step 4: Share with Teammates
Send them: `https://javiql.onrender.com`

They click it, enter their database config, and start using it!

---

## Alternative Deployments

### Railway.app (Also Free)
1. Go to https://railway.app
2. Connect GitHub repo
3. Add environment variables
4. Deploy
5. Get public URL

### Docker (Any Cloud)
```bash
docker build -t javiql .
docker run -p 8000:8000 javiql
```

### Local Company Server
```bash
python main.py
```
Then share the URL with teammates on your network.

---

## Troubleshooting

**Build fails?**
- Update `requirements.txt` versions
- Use Python 3.11 or 3.12

**Database connection fails?**
- Check environment variables are set correctly
- Verify database is accessible from cloud
- For Azure/AWS databases, may need firewall rules

**App times out?**
- Render free tier may sleep after 15 mins of inactivity
- Upgrade to paid plan for always-on

---

## Cost

- **Render free**: $0/month (sleeps after 15 min inactivity)
- **Render paid**: $12/month (always on)
- **Railway free**: $5/month credit
- **AWS free**: Varies (usually $0-10/month for small apps)

---

## Need Help?

1. Check Render build logs for errors
2. Verify environment variables are set
3. Test database connection manually
4. Check app logs in Render dashboard
