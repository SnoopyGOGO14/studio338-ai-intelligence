# WOTSON WhatsApp Bridge

This directory contains a Node.js-based bridge that connects the Python WOTSON agent to WhatsApp using the [Baileys](https://github.com/WhiskeySockets/Baileys) library.

## How It Works

1.  **`bridge.js`**: The main application script.
2.  **Authentication**: On first run, it will generate a QR code in your terminal. You must scan this with your phone (in the WhatsApp app under `Linked Devices`) to log in. Session files will be saved in the `auth_info_baileys` directory to keep you logged in.
3.  **Incoming Messages**: It listens for all incoming WhatsApp messages. When a message is received, it forwards the entire message object as a JSON payload to a webhook endpoint on the Python agent (`http://localhost:8000/whatsapp-webhook` by default).
4.  **Outgoing Messages**: It starts an HTTP server on port `5001`. The Python `whatsapp_service.py` module sends POST requests to the `/send` endpoint on this server to send messages to groups or individuals.

## Setup and Running

1.  **Install Node.js**: Make sure you have Node.js (v16+) and npm installed on your system.

2.  **Install Dependencies**: Navigate to this directory in your terminal and run:
    ```bash
    npm install
    ```

3.  **Run the Bridge**: Start the bridge with:
    ```bash
    npm start
    ```

4.  **Scan QR Code**: The first time you run it, a QR code will appear. Scan it with WhatsApp on your phone to connect.

5.  **Start Python Agent**: Ensure your main Python agent (e.g., the Wotson agent or a Flask/FastAPI server) is running and listening for webhook calls on the configured URL.

## Configuration

-   **Bridge Port**: The port the bridge's API runs on is set to `5001` in `bridge.js`.
-   **Python Webhook**: The URL for the Python agent's webhook is set to `http://localhost:8000/whatsapp-webhook` in `bridge.js`.
-   You can change these values directly in the `bridge.js` file if needed. 