# 📁 Project Structure

## Overview

```

shadowc2-android/
├── agent/                 # Android agent
│   ├── app/              # Main app module
│   ├── core/             # Core functionality
│   ├── features/         # Feature modules
│   └── build.gradle.kts
│
├── web/                   # Web dashboard
│   ├── src/              # Source code
│   ├── public/           # Static files
│   └── package.json
│
├── server/                # Backend server
│   ├── app.py           # Main server
│   ├── api/             # API routes
│   ├── models/          # Database models
│   └── requirements.txt
│
├── templates/             # Build templates
│   ├── android/          # Android templates
│   └── mods/             # Module templates
│
├── docs/                  # Documentation
│   ├── api.md           # API reference
│   ├── deployment.md    # Deployment guide
│   └── architecture.md  # Architecture docs
│
├── docker/                # Docker configs
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── .env                   # Environment config
├── docker-compose.yml    # Docker compose
└── README.md             # Project readme

```

## Module Dependencies

```

agent/
├── core/
│   ├── services/
│   │   ├── ShadowService.kt
│   │   └── C2Service.kt
│   ├── crypto/
│   │   └── Encryption.kt
│   └── persistence/
│       └── Storage.kt
├── features/
│   ├── harvest/
│   │   ├── SMS.kt
│   │   ├── Location.kt
│   │   └── Contacts.kt
│   └── stealth/
│       ├── Hider.kt
│       └── Evasion.kt
└── modules/
└── ModuleLoader.kt

web/
├── components/
│   ├── Dashboard.tsx
│   ├── AgentList.tsx
│   ├── CommandPanel.tsx
│   └── PayloadBuilder.tsx
├── hooks/
│   └── useWebSocket.ts
└── utils/
└── api.ts

server/
├── routes/
│   ├── agents.py
│   ├── commands.py
│   └── payload.py
├── models/
│   ├── agent.py
│   └── command.py
└── services/
├── c2.py
└── builder.py

```

## Key Files

### Agent Files
| File | Purpose |
|------|---------|
| `ShadowService.kt` | Main agent service |
| `C2Client.kt` | Communication handling |
| `HarvestManager.kt` | Data collection |
| `StealthEngine.kt` | Anti-detection |
| `Encryption.kt` | Crypto operations |

### Web Files
| File | Purpose |
|------|---------|
| `Dashboard.tsx` | Main interface |
| `PayloadBuilder.tsx` | APK builder |
| `LiveMap.tsx` | Agent tracking |
| `useWebSocket.ts` | Real-time updates |

### Server Files
| File | Purpose |
|------|---------|
| `app.py` | Main server |
| `payload_builder.py` | APK generation |
| `c2_server.py` | C2 operations |
| `models.py` | Database models |
```