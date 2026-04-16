---
name: iOS Gateway Connection Debug
description: Comprehensive debugging guide for iOS ↔ Gateway WebSocket connection issues
---

# iOS Gateway Connection Debug Skill

## Overview

This skill provides a systematic approach to debugging connection issues between
the iOS app and the Nexus Gateway server. It documents the WebSocket handshake
flow, common failure points, and diagnostic logging patterns.

## Connection Architecture

```
┌─────────────────┐       WebSocket        ┌─────────────────┐
│    iOS App      │ ◄──────────────────► │  Gateway Server  │
│  (NexusKit)     │     ws://127.0.0.1    │    (Node.js)     │
└─────────────────┘        :18789          └─────────────────┘
        │                                          │
        ▼                                          ▼
   GatewayChannel.swift                   server-methods/chat.ts
   GatewayNodeSession.swift               chat-handler.ts
   IOSGatewayChatTransport.swift          websocket-manager.ts
```

## V2 Handshake Protocol

### Phase 1: Challenge Request

1. iOS connects to `ws://127.0.0.1:18789` (simulator) or Gateway URL (device)
2. Gateway sends `connect.challenge` event with a nonce
3. iOS signs the nonce with device token
4. iOS sends signed response via `connect` request

### Phase 2: Authentication

1. Gateway verifies signature against stored device identity
2. On success: Returns `hello-ok` with session info
3. On failure: Returns error (check pairing status)

### Phase 3: Event Subscription

1. iOS calls `listen()` to start receiving server-pushed events
2. Events include: `tick`, `health`, `chat`, `agent`, `seqGap`

## Key Files

### iOS Side

| File                            | Purpose                                           |
| ------------------------------- | ------------------------------------------------- |
| `GatewayChannel.swift`          | Low-level WebSocket connection, frame handling    |
| `GatewayNodeSession.swift`      | High-level session management, event broadcasting |
| `IOSGatewayChatTransport.swift` | Chat-specific transport, event decoding           |
| `ChatViewModel.swift`           | UI state management, event handling               |

### Gateway Side

| File                     | Purpose                                             |
| ------------------------ | --------------------------------------------------- |
| `server-methods/chat.ts` | Chat request handlers (`chat.send`, `chat.history`) |
| `chat-handler.ts`        | Agent dispatch, message storage                     |
| `websocket-manager.ts`   | Connection management, event broadcasting           |

## Diagnostic Logging Points

### Add Debug Logging to GatewayChannel.swift (line ~502)

```swift
case let .event(evt):
    if evt.event == "connect.challenge" { return }
    // Debug: log all events except tick (too noisy)
    if evt.event != "tick" {
        self.logger.error("[DEBUG] GatewayChannel received event: \(evt.event)")
    }
```

### Add Debug Logging to IOSGatewayChatTransport.swift (line ~125)

```swift
case "chat":
    guard let payload = evt.payload else { break }
    print("[IOSGatewayChatTransport] 📩 Received chat event")
    if let chatPayload = try? GatewayPayloadDecoding.decode(
        payload, as: NexusChatEventPayload.self)
    {
        print("[IOSGatewayChatTransport] 📩 Chat event state=\(chatPayload.state ?? "nil") runId=\(chatPayload.runId ?? "nil")")
        continuation.yield(.chat(chatPayload))
    }
```

## Common Issues & Solutions

### Issue 1: "Connecting..." Status Never Resolves

**Symptoms**: App stuck on "Connecting..." status **Causes**:

- Gateway not running
- Wrong host/port (simulator vs device)
- Token not present or invalid

**Debug Steps**:

1. Check if Gateway is running: `lsof -i :18789`
2. Verify simulator uses `127.0.0.1:18789`
3. Check token exists in Keychain/storage
4. Look for `connect.challenge` in logs

**Solution**: Ensure Gateway is running and device is properly paired

### Issue 2: Device Identity Mismatch

**Symptoms**: `DEVICE_MISMATCH` error, connection rejected **Causes**:

- Device was re-paired with different identity
- Stale token in iOS Keychain

**Debug Steps**:

1. Check Gateway devices: `nexus devices`
2. Compare stored `deviceId` with iOS token

**Solution**: Clear iOS token, re-pair device:

```bash
nexus devices remove <deviceId>
# Re-pair via QR code flow
```

### Issue 3: Messages Sent But No Response

**Symptoms**: `chat.send` succeeds, but no agent response appears **Causes**:

- Events not being received (listen loop broken)
- Chat events not being decoded properly
- Session mismatch (wrong sessionKey)

**Debug Steps**:

1. Add event logging (see above)
2. Look for `[DEBUG] GatewayChannel received event: chat`
3. Check if `state=delta` or `state=final` events arrive
4. Verify `runId` matches in `pendingRuns`

**Solution**: Ensure `listen()` is called after connection, verify event
decoding

### Issue 4: Health Checks Fail

**Symptoms**: `healthOK = false`, reconnection loops **Causes**:

- Gateway crashed or restarted
- Network timeout

**Debug Steps**:

1. Check `[IOSGatewayChatTransport] health check OK: true/false`
2. Verify Gateway process is running

**Solution**: Restart Gateway, wait for reconnection

## Chat Event Flow

```
1. User sends message
   └─► ChatViewModel.performSend()
       └─► IOSGatewayChatTransport.sendMessage()
           └─► GatewayNodeSession.request("chat.send", ...)
               └─► WebSocket send

2. Gateway processes request
   └─► chat.ts handleSend()
       └─► dispatchInboundMessage()
           └─► Agent runs, streams response

3. Gateway broadcasts events
   └─► broadcastServerEvent("chat", { state: "delta", runId, ... })
       └─► WebSocket event to all subscribers

4. iOS receives events
   └─► GatewayChannel.handle(.event(evt))
       └─► pushHandler?(.event(evt))
           └─► GatewayNodeSession.handleEvent()
               └─► broadcastServerEvent(evt)
                   └─► IOSGatewayChatTransport.events() stream
                       └─► ChatViewModel.handleTransportEvent()
                           └─► UI updates
```

## Testing Commands

### Verify Gateway is Running

```bash
lsof -i :18789
# Should show node process listening
```

### Test Agent Directly (bypass iOS)

```bash
nexus agent --agent main --local --message "test"
```

### Check Gateway Logs

```bash
tail -f ~/.nexus/logs/gateway.log
```

### Check iOS Simulator Logs

```bash
xcrun simctl spawn 'iPhone 17 Pro' log stream --predicate 'subsystem == "com.nexus"'
```

## Recovery Checklist

- [ ] Gateway running on port 18789
- [ ] iOS app using correct host (127.0.0.1 for simulator)
- [ ] Device token present and valid
- [ ] Pairing completed successfully
- [ ] `listen()` loop active after connection
- [ ] Event stream subscribed in ChatViewModel
- [ ] No session key mismatch

## Related Knowledge Items

- Nexus Mobile (Native Swift & Kotlin Infrastructure)
- Nexus Agent Operating System (AOS)
- Gateway Configuration
