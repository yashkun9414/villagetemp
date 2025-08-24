# Railway Deployment Troubleshooting Guide

## 🚂 Current Issue Resolution

### ❌ **Problem**: Internal Server Error on Railway
- **URL**: https://web-production-2cc37.up.railway.app/dashboard
- **Error**: "Internal Server Error - The server encountered an internal error"
- **Root Cause**: Missing environment variables and direct access to protected route

### ✅ **Solution Applied**:

1. **Added Robust Error Handling**
   - Added fallback responses for template failures
   - Added comprehensive error handlers (404, 500, general exceptions)
   - Added try-catch blocks around all critical routes

2. **Fixed Route Protection**
   - Index route now handles authentication errors gracefully
   - Dashboard route redirects to login on errors
   - Login route has fallback HTML if templates fail

3. **Added Diagnostic Endpoints**
   - `/health` - Enhanced health check with system tests
   - `/debug` - Detailed system information for troubleshooting

4. **Enhanced Environment Variable Handling**
   - Added fallback values for missing environment variables
   - Better error messages when variables are missing

## 🔧 Railway Configuration Required

### Environment Variables to Set in Railway:
```
SECRET_KEY=your-super-secret-key-here
ADMIN_EMAIL=admin@weatheralert.com
ADMIN_PASSWORD=your-secure-password
```

### How to Set Environment Variables in Railway:
1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add each environment variable

## 🔍 Troubleshooting Steps

### Step 1: Check Health Endpoint
Visit: `https://web-production-2cc37.up.railway.app/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Gujarat Weather Alert System",
  "timestamp": "2025-08-24T...",
  "tests": {
    "app_running": true,
    "templates_available": true,
    "static_available": true,
    "csv_data_available": true,
    "shared_data_working": true,
    "environment_vars": {
      "SECRET_KEY": true,
      "ADMIN_EMAIL": true,
      "ADMIN_PASSWORD": true
    }
  }
}
```

### Step 2: Check Debug Information
Visit: `https://web-production-2cc37.up.railway.app/debug`

This will show:
- Python version
- Flask version
- Working directory
- Environment variables status
- File system status

### Step 3: Access Correct URLs

#### ✅ **Correct URLs to Use:**
- **Home Page**: `https://web-production-2cc37.up.railway.app/`
- **Admin Login**: `https://web-production-2cc37.up.railway.app/login`
- **Health Check**: `https://web-production-2cc37.up.railway.app/health`

#### ❌ **Don't Access Directly:**
- `/dashboard` - Requires authentication first

### Step 4: Login Process
1. Go to `/login`
2. Use credentials:
   - Email: `admin@weatheralert.com`
   - Password: (whatever you set in ADMIN_PASSWORD)
3. After successful login, you'll be redirected to `/dashboard`

## 🚨 Common Issues & Solutions

### Issue 1: "Internal Server Error" on Home Page
**Cause**: Missing environment variables or template issues
**Solution**: 
- Check `/health` endpoint first
- Ensure environment variables are set in Railway
- App now has fallback HTML if templates fail

### Issue 2: Can't Access Dashboard
**Cause**: Not logged in
**Solution**: 
- Go to `/login` first
- Use correct admin credentials
- Dashboard requires authentication

### Issue 3: Template Errors
**Cause**: Missing template files or translation issues
**Solution**: 
- App now has fallback HTML responses
- Check `/debug` endpoint for file system status
- All templates should be included in deployment

### Issue 4: Database/Subscription Errors
**Cause**: Missing shared_data.py or file permissions
**Solution**: 
- Check `/health` endpoint for shared_data_working status
- Ensure all Python files are deployed
- Check Railway logs for specific errors

## 📊 System Architecture on Railway

```
Railway Platform
├── Web Service (Port: $PORT)
│   ├── Gunicorn WSGI Server
│   │   └── Flask App (app.py via wsgi.py)
│   ├── Static Files (/static/)
│   ├── Templates (/templates/)
│   └── Data Files (CSV files)
├── Environment Variables
│   ├── SECRET_KEY
│   ├── ADMIN_EMAIL
│   └── ADMIN_PASSWORD
└── Health Monitoring
    └── /health endpoint
```

## 🔄 Deployment Process

1. **Railway Auto-Deploy**:
   - Detects Procfile
   - Installs requirements.txt
   - Runs: `gunicorn --bind 0.0.0.0:$PORT wsgi:application --timeout 120 --workers 1 --log-level info`

2. **Health Check**:
   - Railway checks if service responds on $PORT
   - Our `/health` endpoint provides detailed status

3. **Error Recovery**:
   - If templates fail, fallback HTML is served
   - If database fails, error messages are shown
   - Logs are available in Railway dashboard

## 🎯 Next Steps

1. **Set Environment Variables** in Railway dashboard
2. **Test Health Endpoint**: `/health` should return 200 OK
3. **Access Home Page**: `/` should load without errors
4. **Login as Admin**: `/login` with your credentials
5. **Access Dashboard**: Should work after login

## 📞 Support Information

If issues persist:
1. Check Railway logs in the dashboard
2. Visit `/debug` endpoint for system information
3. Ensure all environment variables are set correctly
4. Verify the bot is running separately (if needed)

The system is now **production-ready** with comprehensive error handling and fallback mechanisms.