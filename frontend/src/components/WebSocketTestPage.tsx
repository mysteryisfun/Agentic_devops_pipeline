import React from 'react';

interface WebSocketTestPageProps {
  onBack: () => void;
}

export const WebSocketTestPage: React.FC<WebSocketTestPageProps> = ({ onBack }) => {
  return (
    <div className="min-h-screen bg-background text-foreground p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <h1 className="text-2xl font-bold">WebSocket Message Tester</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Message Templates */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Test Messages</h2>
            </div>
            
            <div className="space-y-2 max-h-96 overflow-y-auto">
            </div>

            {/* Custom JSON Input */}
            <div className="space-y-2">
              <h3 className="font-medium">Custom JSON Message</h3>
              <textarea
                placeholder="Enter custom JSON message..."
                className="w-full h-32 p-3 bg-muted border border-border rounded-lg font-mono text-sm resize-none"
              />
              <button
                disabled={true}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
              >
                Send Custom Message
              </button>
            </div>
          </div>

          {/* Right Panel - Selected Message & Logs */}
          <div className="space-y-4">
            {/* Selected Message Preview */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">Selected:</h3>
                <button
                  disabled={true}
                  className="px-3 py-1 bg-primary hover:bg-primary/90 disabled:bg-gray-600 text-white rounded text-sm transition-colors"
                >
                  Send Message
                </button>
              </div>
              <pre className="p-3 bg-muted border border-border rounded-lg text-xs overflow-auto max-h-48">
              </pre>
            </div>

            {/* WebSocket Logs */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">WebSocket Logs</h3>
                <button
                  disabled={true}
                  className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm transition-colors"
                >
                  Clear Logs
                </button>
              </div>
              <div className="h-96 p-3 bg-black border border-border rounded-lg overflow-auto font-mono text-xs">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
