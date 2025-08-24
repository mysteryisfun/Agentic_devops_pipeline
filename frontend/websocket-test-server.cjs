#!/usr/bin/env node
/**
 * Simple WebSocket Test Server for Frontend Testing
 * This server accepts all the protocol JSONs and echoes them back
 */

const WebSocket = require('ws');
const http = require('http');

// Create HTTP server
const server = http.createServer();

// Create WebSocket server
const wss = new WebSocket.Server({ 
  server,
  path: '/ws/all'  // Match the protocol endpoint
});

console.log('🚀 WebSocket Test Server Starting...');

// Store connected clients
const clients = new Set();

wss.on('connection', function connection(ws, request) {
  console.log('✅ New WebSocket connection established');
  clients.add(ws);
  
  // Send welcome message
  const welcomeMessage = {
    type: "ack",
    message: "Connected to test server - ready to receive protocol JSONs",
    timestamp: Date.now() / 1000,
    connection_stats: {
      total_connections: clients.size
    }
  };
  ws.send(JSON.stringify(welcomeMessage, null, 2));
  
  // Handle incoming messages
  ws.on('message', function message(data) {
    try {
      const jsonMessage = JSON.parse(data.toString());
      console.log('📨 Received message:', jsonMessage.type || 'unknown');
      
      // Echo back the message with acknowledgment
      const response = {
        type: "test_echo",
        message: `Received and processed: ${jsonMessage.type || 'unknown message'}`,
        original_message: jsonMessage,
        timestamp: Date.now() / 1000,
        status: "success"
      };
      
      ws.send(JSON.stringify(response, null, 2));
      
      // Broadcast to other clients (if any)
      clients.forEach(client => {
        if (client !== ws && client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({
            type: "broadcast",
            message: `Another client sent: ${jsonMessage.type || 'unknown'}`,
            timestamp: Date.now() / 1000
          }));
        }
      });
      
    } catch (error) {
      console.error('❌ Error parsing message:', error);
      ws.send(JSON.stringify({
        type: "error",
        message: "Invalid JSON format",
        timestamp: Date.now() / 1000
      }));
    }
  });
  
  // Handle client disconnect
  ws.on('close', function close() {
    console.log('❌ WebSocket connection closed');
    clients.delete(ws);
  });
  
  // Handle errors
  ws.on('error', function error(err) {
    console.error('❌ WebSocket error:', err);
    clients.delete(ws);
  });
});

// Start the server
const PORT = process.env.PORT || 8000;
server.listen(PORT, function listening() {
  console.log(`✅ WebSocket Test Server running on ws://localhost:${PORT}/ws/all`);
  console.log(`📋 Protocol endpoints available:`);
  console.log(`   - ws://localhost:${PORT}/ws/all (general broadcast)`);
  console.log(`🧪 Ready to test protocol JSONs from frontend!`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('⏹️  Shutting down WebSocket test server...');
  server.close();
});

process.on('SIGINT', () => {
  console.log('\n⏹️  Shutting down WebSocket test server...');
  server.close();
  process.exit(0);
});
