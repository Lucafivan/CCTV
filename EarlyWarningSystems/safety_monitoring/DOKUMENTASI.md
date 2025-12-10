# SAFETY MONITORING SYSTEM - DOKUMENTASI LENGKAP

## 1. PENJELASAN TENTANG SISTEM

### 1.1 Definisi Umum

Safety Monitoring System adalah aplikasi real-time untuk memonitor keselamatan (safety) di lokasi tertentu menggunakan teknologi computer vision dan audio processing. Sistem ini dirancang untuk mendeteksi berbagai kondisi berbahaya dan memberikan alert secara real-time kepada operator.

### 1.2 Komponen Utama

Sistem terdiri dari 3 bagian utama:

#### Backend (Python + FastAPI)
- Server aplikasi yang menjalankan logika deteksi
- WebSocket untuk komunikasi real-time dengan frontend
- Event queue untuk mengelola data dari berbagai sumber (kamera, microphone)
- Database SQLite untuk menyimpan historical data

#### Frontend (React + Vite)
- Web dashboard untuk visualisasi data
- Real-time updates via WebSocket
- Interface untuk melihat statistics dari berbagai camera
- Log table untuk historical events

#### Hardware
- 2 buah kamera USB (webcam)
- 1 buah microphone USB
- Computer untuk menjalankan backend dan frontend

### 1.3 Technology Stack

**Backend:**
- FastAPI (web framework)
- OpenCV (computer vision)
- sounddevice (audio capture)
- SQLite (database)
- Python 3.9+

**Frontend:**
- React (UI framework)
- Vite (build tool)
- Node.js 16+

**Deployment:**
- Docker & Docker Compose
- Python virtual environment

---

## 2. KEGUNAAN SISTEM

### 2.1 Use Case Utama

Sistem ini digunakan untuk:

1. **Monitoring Keselamatan Kerja (Safety)**
   - Deteksi kehadiran orang di area terlarang
   - Deteksi kecelakaan (orang jatuh/berbaring)
   - Monitoring penggunaan safety equipment (PPE)

2. **Monitoring Keamanan (Security)**
   - Deteksi suara alarm atau noise berbahaya
   - Monitoring aktivitas di lokasi tertentu
   - Recording historical data untuk audit

3. **Workplace Safety Compliance**
   - Memastikan worker menggunakan safety equipment
   - Mencatat incident yang terjadi
   - Provide evidence untuk safety audit

### 2.2 Target User

- **Safety Officer** - Monitoring dan response terhadap incidents
- **Facility Manager** - Manage berbagai monitoring points
- **Auditor** - Review historical data untuk compliance
- **Management** - Dashboard dan reporting

### 2.3 Benefit

✅ **Real-time Detection** - Instant alert saat ada anomali
✅ **24/7 Monitoring** - Monitoring tanpa henti
✅ **Historical Data** - Record semua events untuk audit
✅ **Easy Deployment** - Setup dengan Docker
✅ **Scalable** - Bisa handle multiple cameras
✅ **Cost Effective** - Menggunakan open-source technology

---

## 3. CARA KERJA SISTEM

### 3.1 Architecture Overview

```
INPUT LAYER              PROCESSING LAYER           OUTPUT LAYER
┌──────────────┐        ┌──────────────┐           ┌──────────────┐
│ Kamera 0     │        │ CameraWorker │           │              │
│ (People)     │───────→│ (threading)  │──┐        │              │
└──────────────┘        │              │  │        │  WebSocket   │
                        └──────────────┘  │        │  Broadcast   │
┌──────────────┐        ┌──────────────┐  │   ┌───→│              │
│ Kamera 1     │───────→│ CameraWorker │──┤   │    │   Frontend   │
│ (PPE)        │        │ (threading)  │  ├───┤    │   Dashboard  │
└──────────────┘        └──────────────┘  │   │    │              │
                                          │   │    │ • Statistics │
┌──────────────┐        ┌──────────────┐  │   │    │ • Event Log  │
│ Microphone   │───────→│ AudioWorker  │──┤   │    │ • Alerts     │
│              │        │ (threading)  │  │   │    │              │
└──────────────┘        └──────────────┘  │   │    └──────────────┘
                                          ↓   │
                        ┌──────────────────┐  │
                        │ queue.Queue      │  │
                        │ (thread-safe)    │──┤
                        └──────────────────┘  │
                                          ↓   │
                        ┌──────────────────┐  │
                        │ EventProcessor   │  │
                        │ (async loop)     │──┘
                        └──────────────────┘
                                 │
                                 ↓
                        ┌──────────────────┐
                        │ EventLogger      │
                        │ SQLite Database  │
                        └──────────────────┘
```

### 3.2 Data Flow Detail

#### Step 1: Input Capture

**Camera Processing:**
```
Kamera (USB device) 
  → OpenCV reads frame
    → Detector runs
      → Generate event
```

**Audio Processing:**
```
Microphone (USB device)
  → sounddevice captures audio
    → Calculate dB level
      → Generate event
```

#### Step 2: Event Queue

```
Workers (threading)                Event Queue (thread-safe)
├─ CameraWorker                   ┌─────────────────────────┐
│  └─ put_nowait()  ──────────────→ │ queue.Queue(maxsize) │
│                                   │ • Thread-safe         │
├─ AudioWorker                      │ • Non-blocking        │
│  └─ put_nowait()  ──────────────→ │ • FIFO order         │
│                                   └─────────────────────────┘
└─ Running in parallel                       ↓
   (concurrent)                        (get from queue)
```

#### Step 3: Event Processing

```
AsyncIO Event Loop (async)
┌─────────────────────────────┐
│ while True:                 │
│   try:                      │
│     event = queue.get()    │  ← Get from queue (blocking with timeout)
│     logger.log_event()     │  ← Save to database
│     broadcast(event)       │  ← Send to WebSocket clients
│   except queue.Empty:      │
│     sleep briefly          │
└─────────────────────────────┘
```

#### Step 4: Database Storage

```
EventLogger (thread-safe with locks)
┌──────────────────────────┐
│ SQLite Database          │
├──────────────────────────┤
│ Table: events            │
│ ├─ id (PRIMARY KEY)      │
│ ├─ timestamp             │
│ ├─ source (cam0/cam10)   │
│ ├─ event_type            │
│ ├─ payload (JSON)        │
│ └─ created_at            │
│                          │
│ Fallback: CSV logs       │
└──────────────────────────┘
```

#### Step 5: WebSocket Broadcast

```
Backend                              Frontend (Browser)
┌─────────────────────┐             ┌──────────────────┐
│ ConnectionManager   │             │ Dashboard.jsx    │
├─────────────────────┤             ├──────────────────┤
│ active_connections  │             │ WebSocket client │
│ (set of clients)    │ broadcast() │ onmessage()      │
│                     │←───────────→│ setData()        │
│ async broadcast()   │  {message}  │ setLogs()        │
│ sends JSON to all   │             │ render()         │
└─────────────────────┘             └──────────────────┘
```

### 3.3 Detector Details

#### Camera 0: People & Accident Detection

```
Frame Input
    ↓
┌─────────────────────────────┐
│ PeopleDetector              │
├─────────────────────────────┤
│ Method: HOG (Histogram of   │
│ Oriented Gradients)         │
│ Output: people_count        │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ PoseDetector                │
├─────────────────────────────┤
│ Method: Pose Estimation     │
│ Detect: Lying position      │
│ Output: accident_detected   │
└─────────────────────────────┘
    ↓
Generate Event:
{
  'source': 'cam0',
  'type': 'camera_detection',
  'people_count': 5,
  'accident_detected': false,
  'fps': 10
}
```

#### Camera 1: PPE Compliance

```
Frame Input
    ↓
┌─────────────────────────────┐
│ PPEDetector                 │
├─────────────────────────────┤
│ Detect: Safety Equipment    │
│ (helmet, vest, gloves, etc) │
│ Output: compliant/non-      │
│         compliant count     │
└─────────────────────────────┘
    ↓
Generate Event:
{
  'source': 'cam10',
  'type': 'camera_detection',
  'ppe_compliant': 8,
  'ppe_non_compliant': 2,
  'missing_items': ['helmet', 'vest']
}
```

#### Audio: Noise Level Detection

```
Audio Stream (continuous)
    ↓
┌─────────────────────────────┐
│ Calculate dB Level          │
├─────────────────────────────┤
│ RMS (Root Mean Square)      │
│ Convert to dB (decibel)     │
│ Calibrate to 0-120 range    │
└─────────────────────────────┘
    ↓
Check Threshold
    ↓
Generate Event:
{
  'source': 'audio',
  'type': 'noise_level',
  'noise_level': 87.5,
  'threshold': 85,
  'alert': true
}
```

### 3.4 Configuration

File: `backend/config.json`

```json
{
  "cam0_device": 0,              // Camera index (0 = built-in)
  "cam10_device": 1,             // Second camera index
  "noise_threshold": 85,         // dB threshold for alert
  "ppe_detection_enabled": true,
  "accident_detection_enabled": true,
  "log_interval_seconds": 60,    // Database flush interval
  "camera_fps": 10,              // Frames per second (10 = good balance)
  "audio_sample_rate": 44100,    // Audio quality (Hz)
  "audio_chunk_size": 2048,      // Audio buffer size
  "detection_confidence": 0.5    // Model confidence (0.0-1.0)
}
```

### 3.5 API Endpoints

| Endpoint | Method | Fungsi | Response |
|----------|--------|--------|----------|
| `/` | GET | Health check | `{status, service, timestamp}` |
| `/stats` | GET | System stats | `{connected_clients, worker_status}` |
| `/logs` | GET | Recent logs | `{total, logs array}` |
| `/logs/summary` | GET | Statistics | `{total_events, by_source, by_type}` |
| `/ws/dashboard` | WS | Real-time events | Event stream |

### 3.6 Key Features

**1. Multi-threaded Workers**
- CameraWorker (thread 1) - Independent camera processing
- AudioWorker (thread 2) - Independent audio processing
- Both push to thread-safe queue

**2. Event-Driven Architecture**
- Events generated by workers
- Queue manages event flow
- Async processor handles events
- WebSocket broadcasts to clients

**3. Database Logging**
- SQLite for primary storage
- CSV fallback if SQLite fails
- Automatic flushing (60 sec interval)
- Historical data retention

**4. Real-time Updates**
- WebSocket connection (persistent)
- Auto-reconnect on disconnect
- Keep-alive messages (30 sec)
- Server-side broadcast to all clients

**5. Error Handling**
- Specific exception handling (queue.Full)
- Graceful degradation (CSV fallback)
- Thread-safe operations (locks)
- Timeout handling (non-blocking queue.get)

---

## 4. KESIMPULAN

### 4.1 Ringkasan Sistem

Safety Monitoring System adalah solusi monitoring keselamatan berbasis computer vision yang:

✅ **Memanfaatkan teknologi terkini** - OpenCV, FastAPI, WebSocket
✅ **Mudah di-deploy** - Docker & Docker Compose
✅ **Real-time processing** - Event-driven architecture
✅ **Scalable** - Support multiple cameras
✅ **Reliable** - Thread-safe, proper error handling
✅ **Documented** - Clear code structure

### 4.2 Keunggulan

1. **Deteksi Otomatis** - Tidak perlu manual monitoring
2. **24/7 Operation** - Sistem berjalan sepanjang waktu
3. **Data Recording** - Semua events tersimpan di database
4. **Easy Setup** - Setup dalam beberapa menit
5. **Cost Effective** - Open-source, tidak perlu license

### 4.3 Use Cases Potensial

- **Construction Sites** - Monitor safety compliance
- **Factories** - Detect accidents dan unauthorized access
- **Warehouses** - Monitor loading/unloading operations
- **Mining Sites** - Detect hazardous conditions
- **Healthcare Facilities** - Monitor patient safety
- **Public Spaces** - General security monitoring

### 4.4 Cara Menggunakan

**Setup:**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Frontend (terminal baru)
cd frontend
npm install
npm run dev

# Open: http://localhost:5173
```

**Docker:**
```bash
docker-compose up -d
```

**Configuration:**
- Edit `backend/config.json` untuk adjust device indices dan thresholds
- Set `VITE_API_URL` environment variable untuk production

### 4.5 Technical Highlights

**Architecture Patterns:**
- Event-driven architecture
- Producer-consumer pattern (workers → queue → processor)
- Pub-sub pattern (WebSocket broadcast)

**Best Practices:**
- Thread-safe queue communication (queue.Queue)
- Specific exception handling (except queue.Full)
- Atomic database operations (buffer copy before flush)
- Environment-based configuration (not hardcoded)

**Scalability:**
- Multiple cameras support
- Async processing for concurrent clients
- Database batching for efficiency
- Configurable FPS and detection settings

### 4.6 Future Improvements

1. **Machine Learning** - Replace HOG with neural networks (YOLO, MobileNet)
2. **Cloud Integration** - Send alerts to cloud services
3. **Mobile App** - Mobile client for monitoring
4. **Advanced Analytics** - Trend analysis dan predictions
5. **Multi-site Management** - Manage multiple locations
6. **AI-powered Alerts** - Smart alerting based on patterns

### 4.7 Summary

Safety Monitoring System adalah aplikasi production-ready yang menggabungkan computer vision, real-time processing, dan modern web architecture untuk memberikan solusi monitoring keselamatan yang comprehensive dan reliable.

Sistem ini:
- Menggunakan teknologi open-source
- Mudah di-setup dan di-deploy
- Thread-safe dan production-ready
- Well-structured dan maintainable
- Siap untuk production use

---

## Support & Documentation

Untuk bantuan lebih lanjut:
1. Check backend logs: `backend/logs/safety_logs.db`
2. Check frontend console: Browser DevTools
3. Review configuration: `backend/config.json`
4. Check API docs: `http://localhost:8000/docs` (Swagger UI)

---

**Last Updated:** December 10, 2025
**Version:** 1.0
**Status:** Production Ready ✅
