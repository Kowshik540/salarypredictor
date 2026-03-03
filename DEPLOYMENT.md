# 🚀 Know Your Worth — Full Deployment Guide

## Architecture Overview

```
Browser (Netlify/GitHub Pages)
        ↕  HTTPS API calls
Flask Backend (Render)
        ↕  MongoDB Atlas (cloud DB)
        ↕  Gmail SMTP (email verification)
```

---

## Step 1 — Push to GitHub

1. Create a new GitHub repo: `know-your-worth`
2. In your project folder, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/know-your-worth.git
   git push -u origin main
   ```

> ⚠️ Make sure `.env` is in `.gitignore` — never push secrets to GitHub!

---

## Step 2 — MongoDB Atlas (Database)

Your MongoDB Atlas is already set up (from your `.env`). Just verify:

1. Go to [cloud.mongodb.com](https://cloud.mongodb.com)
2. **Network Access** → Add IP: `0.0.0.0/0` (allow all — needed for Render)
3. Your connection string is already in `.env.example`

The app uses:
- **Database**: `AI_Salar_Predictor`
- **Collection**: `users`  
  Each document: `{ email, password, verified: true/false }`

---

## Step 3 — Deploy Backend to Render

1. Go to [render.com](https://render.com) → **New → Web Service**
2. Connect your GitHub repo
3. Set these settings:

   | Setting | Value |
   |---|---|
   | **Root Directory** | `back-end` |
   | **Runtime** | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn server:app --bind 0.0.0.0:$PORT` |

4. Add **Environment Variables** (one by one):

   | Key | Value |
   |---|---|
   | `MONGO_URI` | `mongodb+srv://kowshikthota43_db_user:KowshikIPS12@cluster0.1dcplhh.mongodb.net/...` |
   | `SECRET_KEY` | `SUPER_SECRET_KEY_123` (use something stronger in prod) |
   | `MAIL_USERNAME` | `kowshikthota43@gmail.com` |
   | `MAIL_PASSWORD` | `napg irbo zafd dgbi` |
   | `APP_URL` | `https://YOUR-APP-NAME.onrender.com` ← set after first deploy |

5. Click **Deploy**. Wait ~3 mins for first build.
6. Copy your Render URL (e.g. `https://know-your-worth-api.onrender.com`)

> 💡 **Free tier note**: Render free services sleep after 15 min of inactivity.
> First request after sleep takes ~30 seconds. Upgrade to $7/mo to avoid this.

---

## Step 4 — Update Frontend API URL

After you have your Render URL, update **3 files** in `front-end/`:

In `index.html`, `login.html`, and `signup.html`, find:
```javascript
: "https://YOUR-RENDER-APP-NAME.onrender.com";
```
Replace with your actual URL:
```javascript
: "https://know-your-worth-api.onrender.com";
```

Then commit and push again:
```bash
git add front-end/
git commit -m "Set production API URL"
git push
```

---

## Step 5 — Deploy Frontend

### Option A: Netlify (Recommended — easiest)

1. Go to [netlify.com](https://netlify.com) → **Add new site → Import from Git**
2. Connect your GitHub repo
3. Set:
   - **Base directory**: `front-end`
   - **Publish directory**: `front-end`
   - Build command: *(leave empty)*
4. Click **Deploy site**
5. Your site is live at `https://random-name.netlify.app`
6. (Optional) Add custom domain in Netlify settings

### Option B: GitHub Pages

1. Go to your repo → **Settings → Pages**
2. Source: **Deploy from branch**
3. Branch: `main`, Folder: `/front-end`
4. Save → site available at `https://YOUR_USERNAME.github.io/know-your-worth/`

---

## Step 6 — Update APP_URL in Render

Once your frontend is live:
1. Go back to Render → Environment Variables
2. Update `APP_URL` to your Netlify/GitHub Pages URL
   - This ensures verification email links point to your live app

---

## ✅ Final Checklist

- [ ] GitHub repo created and code pushed
- [ ] `.env` NOT committed to GitHub
- [ ] MongoDB Atlas Network Access allows `0.0.0.0/0`
- [ ] Render backend deployed and running
- [ ] All 3 HTML files updated with Render URL
- [ ] Frontend deployed on Netlify or GitHub Pages
- [ ] Test signup → check email → verify → login → predict salary

---

## 🛠 Troubleshooting

| Problem | Fix |
|---|---|
| Render build fails | Check `requirements.txt` versions; check build logs |
| MongoDB connection error | Verify IP whitelist `0.0.0.0/0` in Atlas |
| Email not sending | Re-generate Gmail App Password (16-char code from Google Account → Security → App Passwords) |
| Login says "verify email" | Click verification link in inbox; check spam folder |
| PDF download fails | Check Render logs for `reportlab` import errors |
| CORS error in browser | Make sure `flask-cors` is installed and `CORS(app, origins="*")` is in server.py |

---

## 🔐 Security Notes for Production

- Replace `SECRET_KEY` with a long random string: `python -c "import secrets; print(secrets.token_hex(32))"`
- Consider hashing passwords with `bcrypt` instead of storing plaintext
- Add rate limiting with `flask-limiter` to prevent abuse
- Use HTTPS everywhere (Render and Netlify both provide this automatically)
