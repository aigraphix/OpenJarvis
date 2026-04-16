---
name: gateway-protocol
description: Essential protocol specification for connecting to the Nexus Gateway WebSocket. Use when implementing or debugging WebSocket clients (e.g., chat sidebars, dashboards, or agents) to ensure proper handshake, authentication, and message framing.
---

# Gateway Protocol Mastery 📡

This skill documents the **Nexus Gateway Protocol** (v3). Failure to follow
these strict constants will result in `INVALID_REQUEST` or silent connection
drops.

## 🤝 The Mandatory Handshake

Every WebSocket connection MUST begin with a `connect` request frame.

### Handshake Constants (Strict)

- **`platform`**: Must be `'web'` for browser clients.
- **`id`**: Use `'webchat-ui'` for the Mission Control chat.
- **`mode`**: Use `'webchat'` for interactive sessions.
- **`minProtocol` / `maxProtocol`**: Must be `3`.

### Example Handshake Request

```javascript
{
  "type": "req",
  "method": "connect",
  "id": "handshake",
  "params": {
    "client": {
      "platform": "web",
      "id": "webchat-ui",
      "mode": "webchat",
      "version": "1.0.0"
    },
    "auth": { 
      "token": "GATEWAY_TOKEN" 
    },
    "minProtocol": 3,
    "maxProtocol": 3
  }
}
```

## 🏗️ Message Framing

All messages follow a discriminator pattern:

1. **`type: "req"`**: Outbound request (requires `method` and `id`).
2. **`type: "res"`**: Server response (matches `id`, includes `ok: true/false`).
3. **`type: "event"`**: One-way broadcast (includes `event` and `payload`).

### Common Methods

- **`chat.history`**: Fetch past messages.
  - Params: `{ "sessionKey": "...", "limit": 50 }`
- **`chat.send`**: Send a message.
  - Params: `{ "sessionKey": "...", "message": "...", "idempotencyKey": "..." }`

## 📨 Event Handling (Streaming)

Real-time responses arrive as `chat` events.

### Payload Structure

```javascript
{
  "type": "event",
  "event": "chat",
  "payload": {
    "state": "delta" | "final" | "error",
    "runId": "...",
    "message": {
      "role": "assistant",
      "content": [{ "type": "text", "text": "..." }]
    }
  }
}
```

### Rendering Rules

- **Text Extraction**: The `message.content` is an **array of objects**. You
  must map over it to join the `text` fields.
- **Deltas**: When `state === 'delta'`, append the text to your local buffer for
  that `runId`.
- **Final**: When `state === 'final'`, replace the local buffer with the
  snapshot for total parity.
