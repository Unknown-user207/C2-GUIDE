# 📡 Communication Channels

## Channel Architecture

### Primary Channel: HTTPS
```

Agent ───► HTTPS (443) ───► C2 Server
├── Certificate Pinning
├── Encrypted Payloads
└── Random User-Agents

```

### Secondary Channel: WebSocket
```

Agent ───► WebSocket (wss://) ───► C2 Server
├── Real-time Commands
├── Bidirectional
└── Low Latency

```

### Fallback Channels

#### 1. Firebase Cloud Messaging (FCM)
```

Agent ───► FCM ───► Google Servers ───► C2 Server
└── Push notifications as commands

```

#### 2. DNS Tunneling
```

Agent ───► DNS Queries ───► DNS Server ───► C2 Server
└── Encoded commands in subdomains

```

#### 3. SMS Channel
```

Agent ───► SMS ───► GSM Network ───► C2 Server
└── Encrypted text messages

```

#### 4. Bluetooth (Local)
```

Agent ───► Bluetooth ───► Nearby Device
└── Local mesh network

```

## Communication Flow

### 1. Agent Beacon
```

Agent → [Collect Device Info] → [Encrypt] → [Send]
→ [Wait for Commands] → [Execute] → [Return Results]

```

### 2. Command Execution
```

C2 → [Enqueue Command] → [Send to Agent] 
→ [Agent Executes] → [Returns Result]
→ [C2 Updates Status]

```

### 3. Fallback Strategy
```

HTTPS Failed → WebSocket Failed → FCM Failed 
→ DNS Failed → SMS Failed → Bluetooth (Local) → Staggered Beacons

```

## Encryption Layers

### Layer 1: Transport (TLS 1.3)
- HTTPS encryption
- Certificate pinning
- Perfect forward secrecy

### Layer 2: Application (AES-256-GCM)
- Payload encryption
- Key rotation
- Random IV generation

### Layer 3: Steganography
- Hidden in images
- Hidden in traffic patterns
- Hidden in timing
```