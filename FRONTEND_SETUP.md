# Frontend Setup Guide

## Architecture

The application now uses a **modern Next.js frontend** with a **Flask API backend**:

- **Frontend**: Next.js 16 (TypeScript, Tailwind CSS) - Port 3000
- **Backend**: Flask API (Python) - Port 5001
- **Design**: Modern glass morphism with dark theme, no gradients/emojis, icon-based UI

## Quick Start

### 1. Install Backend Dependencies

```bash
# From project root
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Configure Environment

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:5001
```

### 4. Run Both Servers

**Terminal 1 - Backend (Flask API):**
```bash
# From project root
./start.sh
```

**Terminal 2 - Frontend (Next.js):**
```bash
cd frontend
npm run dev
```

### 5. Access the App

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001

## Project Structure

```
BankTransact/
├── frontend/              # Next.js frontend
│   ├── app/              # Next.js app router
│   │   ├── page.tsx      # Home page
│   │   ├── hdfc/         # HDFC processing page
│   │   └── axis/         # AXIS processing page
│   ├── components/       # React components
│   ├── lib/              # API client
│   └── package.json
│
├── web/                  # Flask API backend
│   ├── app.py            # Flask API server
│   ├── uploads/          # Temporary uploads
│   └── outputs/          # Processed files
│
└── src/                  # Business logic
    ├── HDFC/
    └── AXIS/
```

## Features

### Design
- ✅ Clean, professional, minimalistic
- ✅ Glass morphism effects
- ✅ Dark theme
- ✅ No gradients or emojis
- ✅ Icon-based UI (SVG icons)
- ✅ Responsive design

### Functionality
- ✅ Drag & drop file upload
- ✅ Multiple file processing
- ✅ Real-time status updates
- ✅ Account mapping configuration (HDFC)
- ✅ Download processed files
- ✅ Party analysis (AXIS)

## Development

### Frontend Development
```bash
cd frontend
npm run dev      # Development server
npm run build    # Production build
npm run start    # Production server
```

### Backend Development
```bash
# From project root
./start.sh       # Development server
```

## API Endpoints

All API endpoints are under `/api/`:

- `POST /api/upload/<bank_type>` - Upload files
- `POST /api/process/<bank_type>` - Process statements
- `GET /api/download/<filename>` - Download files
- `GET /api/config/hdfc/account-mapping` - Get account mapping
- `POST /api/config/hdfc/account-mapping` - Update account mapping

## Migration Notes

- Old HTML templates in `web/templates/` are still available for reference
- Flask app is now API-only (no template rendering)
- CORS is enabled for Next.js frontend
- Both servers must run simultaneously

## Troubleshooting

### CORS Errors
Make sure `flask-cors` is installed:
```bash
pip install flask-cors
```

### Port Conflicts
- Backend: Change port in `start.sh` or set `PORT` environment variable
- Frontend: Change port with `npm run dev -- -p 3001`

### API Connection Issues
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Ensure backend is running on the correct port
- Check browser console for CORS errors

