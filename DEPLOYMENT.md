# Deployment Guide

## 🎯 Recommendation: **Heroku** (Not Netlify)

### Why Heroku?
- ✅ **Native Python/Flask support** - Built for backend applications
- ✅ **Handles file uploads** - Can process large Excel/CSV files
- ✅ **Persistent storage options** - For temporary file storage
- ✅ **Easy Git deployment** - Simple `git push` workflow
- ✅ **Free tier available** - Good for testing (with limitations)

### Why NOT Netlify?
- ❌ **Static sites only** - Designed for frontend, not Flask backends
- ❌ **Limited serverless** - Not suitable for file processing workloads
- ❌ **No Python runtime** - Can't run Flask applications natively

## 🚀 Quick Deploy to Heroku

### Prerequisites
1. **Heroku account**: Sign up at https://heroku.com (free)
2. **Heroku CLI**: Install from https://devcenter.heroku.com/articles/heroku-cli
3. **Git repository**: Your code should be in Git

### Step-by-Step Deployment

```bash
# 1. Login to Heroku
heroku login

# 2. Create a new Heroku app
heroku create banktransact-app

# 3. Deploy your code
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main

# 4. Open your app
heroku open
```

That's it! Your app will be live at `https://banktransact-app.herokuapp.com`

## 📋 Files Already Created

I've prepared these files for you:

✅ **`Procfile`** - Tells Heroku how to run your app
✅ **`runtime.txt`** - Specifies Python version
✅ **`requirements.txt`** - Updated with gunicorn (production server)
✅ **`web/app.py`** - Updated to support Heroku's PORT environment variable

## 🔒 Security Warning ⚠️

**This app processes sensitive financial data!**

### Before deploying publicly, you MUST add:

1. **Authentication** - Users must login
2. **HTTPS** - Heroku provides this automatically
3. **Rate Limiting** - Prevent abuse
4. **File Size Limits** - Already set (100MB)
5. **Automatic Cleanup** - Already implemented

### Recommended Security Additions:

```python
# Add to web/app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Add authentication (Flask-Login, etc.)
# Add CSRF protection
# Add file encryption for sensitive uploads
```

## 🌐 Alternative Platforms

### Railway (Recommended Alternative)
- ✅ **Easier setup** than Heroku
- ✅ **$5 free credit/month**
- ✅ **Better file handling**
- ✅ **Simple Git deployment**

**Deploy to Railway:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up
```

### Render
- ✅ Free tier available
- ✅ Good Flask support
- ✅ Automatic SSL

### Fly.io
- ✅ Global deployment
- ✅ Good performance
- ✅ Free tier

## 📊 Platform Comparison

| Feature | Heroku | Netlify | Railway | Render |
|---------|--------|---------|---------|--------|
| Flask Support | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| File Uploads | ✅ Yes | ❌ Limited | ✅ Yes | ✅ Yes |
| Free Tier | ✅ Limited | ✅ Yes | ✅ $5/mo | ✅ Limited |
| Ease of Use | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Best For | Production | Static Sites | Development | Small Apps |

## 🛠 Local Testing (Production Mode)

Test your app locally with production settings:

```bash
# Install gunicorn
pip install gunicorn

# Run in production mode
cd /Users/arpitgupta/Downloads/apps/Concepts/personal/BankTransact
gunicorn web.app:app --bind 0.0.0.0:5001
```

## 💡 Heroku Commands Reference

```bash
# Create app
heroku create your-app-name

# View logs
heroku logs --tail

# Restart app
heroku restart

# Set environment variables
heroku config:set KEY=value

# View config
heroku config

# Open app
heroku open

# Scale dynos (if needed)
heroku ps:scale web=1
```

## ⚠️ Important Notes

### Free Tier Limitations (Heroku)
- **Sleeps after 30 min inactivity** - First request will be slow
- **550 hours/month free** - Enough for testing
- **Ephemeral filesystem** - Files deleted on restart
- **No persistent storage** - Use add-ons for file storage

### For Production Use:
1. **Upgrade to paid tier** ($7/month minimum)
2. **Add persistent storage** (S3, etc.)
3. **Add authentication** (CRITICAL!)
4. **Set up monitoring**
5. **Configure backups**

## 🔐 Security Checklist

Before deploying:
- [ ] Add user authentication
- [ ] Add rate limiting
- [ ] Encrypt sensitive file uploads
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS (automatic on Heroku)
- [ ] Add CSRF protection
- [ ] Set up file cleanup
- [ ] Test security locally

## 📝 Next Steps

1. **Test locally** with gunicorn
2. **Add authentication** before deploying
3. **Deploy to Heroku** using commands above
4. **Test deployed app** thoroughly
5. **Monitor logs** for errors

---

**For sensitive financial data, consider:**
- Private/self-hosted deployment
- VPN-protected access
- Enhanced encryption
- Regular security audits
