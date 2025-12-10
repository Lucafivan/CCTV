# Quick Start Guide

Get the Safety Monitoring System up and running in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Node.js 16+ installed
- Webcam (built-in or USB)
- Microphone (built-in or USB)

## Installation Steps

### 1. Clone or Download the Project

```bash
cd safety-monitoring
```

### 2. Backend Setup (Terminal 1)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python app.py
```

✅ Backend should now be running on **http://localhost:8000**

### 3. Frontend Setup (Terminal 2)

```bash
# Navigate to frontend (open new terminal)
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

✅ Frontend should now be running on **http://localhost:5173**

### 4. Access the Dashboard

Open your browser and go to:
```
http://localhost:5173
```

You should see the Safety Monitoring Dashboard with:
- Camera 0 stats (People & Accidents)
- Camera 10 stats (PPE Compliance)
- Audio monitoring (Noise levels)
- Real-time event logs

## Quick Test

To verify everything is working:

1. **Check Camera Access**: Wave your hand in front of the camera - you should see people count increase
2. **Check Audio**: Clap or make noise - you should see the noise level spike
3. **Check Logs**: The event log table should show incoming events

## Troubleshooting

### Camera Not Working

```bash
# Check available cameras
python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"
```

Then update `backend/config.json`:
```json
{
  "cam0_device": 0,  // Change to your camera index
  "cam10_device": 1  // Change to your second camera index
}
```

### Audio Not Working

```bash
# List audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### WebSocket Connection Failed

Make sure:
1. Backend is running on port 8000
2. No firewall blocking the connection
3. Check browser console for errors

### Dependencies Error

If you get import errors:

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules
npm install
```

## Using Docker (Alternative)

If you prefer Docker:

```bash
# Start everything with one command
docker-compose up --build
```

Then access:
- Dashboard: http://localhost:5173
- Backend: http://localhost:8000

## Configuration

Edit `backend/config.json` to customize:

```json
{
  "cam0_device": 0,           // Primary camera
  "cam10_device": 1,          // Secondary camera
  "noise_threshold": 85,      // dB threshold for alerts
  "camera_fps": 10,           // Processing FPS
  "detection_confidence": 0.5 // Detection threshold
}
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Add trained models to `backend/models/` directory
- Customize detection logic in `backend/detectors/`
- Adjust UI styling in `frontend/src/styles.css`

## Support

If you encounter issues:
1. Check the logs in `logs/` directory
2. Verify all dependencies are installed
3. Make sure cameras and microphone permissions are granted

## Key Features to Test

✅ **People Detection**: Walk in front of camera
✅ **Accident Detection**: Simulate a fall (carefully!)
✅ **PPE Detection**: Wear/remove safety equipment
✅ **Noise Monitoring**: Create loud noises
✅ **Real-time Updates**: Watch the dashboard update live

Happy monitoring! 🎉