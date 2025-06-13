const makeWASocket = require('@whiskeysockets/baileys').default;
const { DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const express = require('express');
const pino = require('pino');
const qrcode = require('qrcode-terminal');
const http = require('http');

const PORT = 5001; // Port for this bridge's API
const PYTHON_WEBHOOK_URL = 'http://localhost:8000/whatsapp-webhook'; // URL of your Python agent's listener

// --- Express App for Sending Messages ---
const app = express();
app.use(express.json());

let sock; // To hold the socket connection

app.post('/send', async (req, res) => {
    const { to, message, type } = req.body;
    if (!to || !message || !type) {
        return res.status(400).json({ error: 'Missing parameters: to, message, type are required.' });
    }

    try {
        if (type === 'group') {
            await sock.sendMessage(to, { text: message });
        } else if (type === 'private') {
            // Ensure the user ID is correctly formatted
            const formattedTo = to.includes('@s.whatsapp.net') ? to : `${to}@s.whatsapp.net`;
            await sock.sendMessage(formattedTo, { text: message });
        } else {
            return res.status(400).json({ error: 'Invalid message type specified.' });
        }
        res.status(200).json({ success: true, message: 'Message sent successfully.' });
    } catch (e) {
        console.error('Failed to send message:', e);
        res.status(500).json({ success: false, error: e.message });
    }
});


// --- Baileys WhatsApp Connection ---
async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    
    sock = makeWASocket({
        auth: state,
        logger: pino({ level: 'silent' })
    });

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        if (qr) {
            console.log("QR Code received, please scan:");
            qrcode.generate(qr, { small: true });
        }
        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Connection closed due to ', lastDisconnect.error, ', reconnecting ', shouldReconnect);
            if (shouldReconnect) {
                connectToWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('WhatsApp connection opened');
        }
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('messages.upsert', async m => {
        const msg = m.messages[0];
        if (!msg.key.fromMe && m.type === 'notify') {
            console.log('Received message:', JSON.stringify(msg, undefined, 2));

            // Forward to Python agent's webhook
            try {
                const postData = JSON.stringify(msg);
                const options = {
                    hostname: 'localhost',
                    port: 8000,
                    path: '/whatsapp-webhook',
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Content-Length': Buffer.byteLength(postData)
                    }
                };
                
                const req = http.request(options, (res) => {
                    console.log(`Python webhook response status: ${res.statusCode}`);
                });

                req.on('error', (e) => {
                    console.error(`Problem with request to Python webhook: ${e.message}`);
                });

                req.write(postData);
                req.end();
                
            } catch (e) {
                console.error('Failed to forward message to Python webhook:', e);
            }
        }
    });
}

// --- Start Server and Connection ---
app.listen(PORT, () => {
    console.log(`WhatsApp bridge API listening on port ${PORT}`);
    connectToWhatsApp();
}); 