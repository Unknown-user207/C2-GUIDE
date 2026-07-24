# 🏗️ Android Architecture Overview

## High-Level Architecture

```

┌─────────────────────────────────────────────────────────┐
│                   Web Dashboard                        │
│              (React + TypeScript)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  Control    │  │  Payload    │  │  Real-time  │  │
│  │  Panel      │  │  Builder    │  │  Map        │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│                  Backend Server                        │
│               (Python Flask)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  API        │  │  WebSocket  │  │  Payload    │  │
│  │  Endpoints  │  │  Server     │  │  Builder    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│                 C2 Communication                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  HTTPS      │  │  WebSocket  │  │  FCM/DNS    │  │
│  │  Channel    │  │  Channel    │  │  Channel    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│                 Android Agent                          │
│                  (Kotlin)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  Core       │  │  Harvest    │  │  Stealth    │  │
│  │  Service    │  │  Modules    │  │  Engine     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘

```

## Key Components

### 1. Android Agent (Kotlin)
- **Core Service**: Main background service
- **Harvest Modules**: SMS, Location, Contacts, Camera
- **C2 Client**: Multi-channel communication
- **Stealth Engine**: Anti-detection mechanisms
- **Persistence**: Boot, scheduled tasks, alarms

### 2. C2 Communication
- **Primary**: HTTPS with certificate pinning
- **Secondary**: WebSocket for real-time commands
- **Fallback**: FCM, DNS tunneling, SMS
- **Encryption**: AES-256 + RSA hybrid

### 3. Web Dashboard
- **Control**: Command sending, agent management
- **Monitoring**: Real-time status, location tracking
- **Payload Builder**: APK generation with options
- **Analytics**: Agent statistics, operational metrics

## Key Technologies

| Layer | Technology | Purpose |
|-------|------------|---------|
| Agent | Kotlin + Coroutines | Android app development |
| Agent Storage | Room / DataStore | Local persistence |
| Agent Network | OkHttp + Retrofit | HTTP communication |
| Web Frontend | React + TypeScript | User interface |
| Web UI | Tailwind CSS | Styling |
| Web Realtime | Socket.io | WebSocket communication |
| Backend | Python Flask | API server |
| Backend Realtime | Flask-SocketIO | WebSocket server |
| Build System | Gradle (Kotlin DSL) | APK building |
| Obfuscation | ProGuard / R8 | Code protection |
```