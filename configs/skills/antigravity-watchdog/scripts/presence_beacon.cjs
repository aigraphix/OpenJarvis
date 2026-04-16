#!/usr/bin/env node
/**
 * presence_beacon.js
 *
 * A small Gateway WebSocket client that:
 *  - waits for `connect.challenge`
 *  - replies with a `connect` request (including a stable device identity)
 *  - sends a periodic `system-event` “presence beacon” every 60s
 *
 * Usage:
 *   npm i ws
 *   node presence_beacon.js
 *
 * Env:
 *   GATEWAY_URL=ws://127.0.0.1:18789        (default)
 *   GATEWAY_TOKEN=...                       (optional; if your gateway requires auth)
 *   CLIENT_ID=antigravity-ide
 *   CLIENT_VERSION=0.1.0
 *   CLIENT_PLATFORM=macos
 *   CLIENT_MODE=ui                          (IMPORTANT: avoid "cli" mode; CLI mode is not shown in presence)
 *   INSTANCE_ID=antigravity:<uuid>          (stable across restarts; default: persisted in .presence_beacon_state.json)
 *   BEACON_INTERVAL_MS=60000
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

const WebSocket = require('ws');

const GATEWAY_URL = process.env.GATEWAY_URL || 'ws://127.0.0.1:18789';
const GATEWAY_TOKEN = process.env.GATEWAY_TOKEN || process.env.NEXUS_GATEWAY_TOKEN || '';

const CLIENT_ID = process.env.CLIENT_ID || 'nexus-probe';
const CLIENT_VERSION = process.env.CLIENT_VERSION || '0.1.0';
const CLIENT_PLATFORM = process.env.CLIENT_PLATFORM || process.env.NODE_PLATFORM || process.platform;
const CLIENT_MODE = process.env.CLIENT_MODE || 'ui';

const BEACON_INTERVAL_MS = Number(process.env.BEACON_INTERVAL_MS || 60_000);

// --- persistence (stable instanceId + keypair) ---

const STATE_PATH = path.resolve(process.cwd(), '.presence_beacon_state.json');

function loadState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_PATH, 'utf8'));
  } catch {
    return {};
  }
}

function saveState(state) {
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}

function ensureInstanceId(state) {
  if (process.env.INSTANCE_ID) return process.env.INSTANCE_ID;
  if (state.instanceId) return state.instanceId;
  const id = `antigravity:${crypto.randomUUID()}`;
  state.instanceId = id;
  saveState(state);
  return id;
}

function ensureEd25519Keys(state) {
  if (state.ed25519 && state.ed25519.privateKeyPem && state.ed25519.publicKeyPem) {
    return state.ed25519;
  }

  const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519');
  const publicKeyPem = publicKey.export({ format: 'pem', type: 'spki' });
  const privateKeyPem = privateKey.export({ format: 'pem', type: 'pkcs8' });

  const kid = crypto
    .createHash('sha256')
    .update(publicKey.export({ format: 'der', type: 'spki' }))
    .digest('hex')
    .slice(0, 24);

  state.ed25519 = { kid, publicKeyPem, privateKeyPem };
  saveState(state);
  return state.ed25519;
}

function base64(buf) {
  return Buffer.from(buf).toString('base64');
}

function signNonce(privateKeyPem, nonce) {
  // The gateway expects a signature over the server-provided nonce.
  // If your gateway expects a different signing payload, adjust here.
  const msg = Buffer.from(String(nonce), 'utf8');
  const sig = crypto.sign(null, msg, privateKeyPem);
  return base64(sig);
}

function makeDeviceId(publicKeyPem) {
  // Stable device id derived from the public key.
  const der = crypto.createPublicKey(publicKeyPem).export({ format: 'der', type: 'spki' });
  return crypto.createHash('sha256').update(der).digest('hex');
}

// --- WS protocol helpers ---

function makeReq(id, method, params) {
  return { type: 'req', id, method, params };
}

function nowMs() {
  return Date.now();
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

// --- main loop ---

async function run() {
  const state = loadState();
  const instanceId = ensureInstanceId(state);
  const keys = ensureEd25519Keys(state);
  const deviceId = makeDeviceId(keys.publicKeyPem);

  let backoffMs = 500;

  for (;;) {
    try {
      await connectAndBeacon({ instanceId, keys, deviceId });
      backoffMs = 500;
    } catch (err) {
      console.error('[presence-beacon] disconnected/error:', err?.message || err);
      await sleep(backoffMs);
      backoffMs = Math.min(backoffMs * 2, 10_000);
    }
  }
}

async function connectAndBeacon({ instanceId, keys, deviceId }) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(GATEWAY_URL);

    let connected = false;
    let beaconTimer = null;
    let lastChallenge = null;

    function cleanup() {
      if (beaconTimer) clearInterval(beaconTimer);
      beaconTimer = null;
      try { ws.close(); } catch {}
    }

    ws.on('open', () => {
      // Wait for connect.challenge, then send connect.
    });

    ws.on('message', (data) => {
      let msg;
      try {
        msg = JSON.parse(String(data));
      } catch {
        return;
      }

      if (msg?.type === 'event' && msg?.event === 'connect.challenge') {
        lastChallenge = msg.payload;

        const signedAt = nowMs();
        const signature = signNonce(keys.privateKeyPem, lastChallenge.nonce);

        const connectParams = {
          minProtocol: 3,
          maxProtocol: 3,
          client: {
            id: CLIENT_ID,
            version: CLIENT_VERSION,
            platform: CLIENT_PLATFORM,
            mode: CLIENT_MODE,
            instanceId,
          },
          role: 'operator',
          scopes: ['operator.read'],
          caps: [],
          commands: [],
          permissions: {},
          locale: 'en-US',
          userAgent: `presence_beacon/${CLIENT_VERSION}`,
          auth: GATEWAY_TOKEN ? { token: GATEWAY_TOKEN } : undefined,
          device: {
            id: deviceId,
            publicKey: base64(Buffer.from(keys.publicKeyPem)),
            signature,
            signedAt,
            nonce: lastChallenge.nonce,
          },
        };

        ws.send(JSON.stringify(makeReq(crypto.randomUUID(), 'connect', connectParams)));
        return;
      }

      if (msg?.type === 'res' && msg?.ok === true && msg?.payload?.type === 'hello-ok') {
        connected = true;
        console.error('[presence-beacon] connected:', {
          instanceId,
          policy: msg.payload.policy,
          protocol: msg.payload.protocol,
        });

        // Start periodic system-event beacons.
        const sendBeacon = () => {
          const payload = {
            kind: 'presence.beacon',
            source: 'antigravity-watchdog',
            instanceId,
            host: os.hostname(),
            ts: nowMs(),
            mode: CLIENT_MODE,
            tags: ['antigravity', 'ide'],
            // Optionally add your own activity signal:
            // lastInputSeconds: <number>
          };

          const req = makeReq(crypto.randomUUID(), 'system-event', payload);
          try {
            ws.send(JSON.stringify(req));
          } catch (e) {
            // If send fails, the close handler will trigger reconnect.
          }
        };

        sendBeacon();
        beaconTimer = setInterval(sendBeacon, BEACON_INTERVAL_MS);
        return;
      }

      // If connect failed, the server returns ok:false and then closes.
      if (msg?.type === 'res' && msg?.ok === false) {
        console.error('[presence-beacon] connect error:', msg.error || msg);
      }
    });

    ws.on('close', () => {
      cleanup();
      if (connected) return resolve();
      return reject(new Error('socket closed before hello-ok'));
    });

    ws.on('error', (err) => {
      cleanup();
      return reject(err);
    });
  });
}

run().catch((e) => {
  console.error('[presence-beacon] fatal:', e);
  process.exit(1);
});
