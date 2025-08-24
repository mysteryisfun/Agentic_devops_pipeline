import { useEffect, useRef, useState, useCallback } from 'react';

// Define the WebSocket message types based on the protocol
export interface WebSocketMessage {
  type: 'pipeline_start' | 'stage_start' | 'status_update' | 'stage_complete' | 'pipeline_complete';
  pipeline_id: string;
  timestamp: string;
  stage?: string;
  status?: 'in_progress' | 'completed' | 'failed';
  data?: any;
  results?: any;
  agent_type?: 'build' | 'analyze' | 'test' | 'deploy' | 'monitor';
  message?: string;
}

interface UseWebSocketProps {
  url: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

export const useWebSocket = ({
  url,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
  autoReconnect = true,
  reconnectInterval = 3000,
}: UseWebSocketProps) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    try {
      // Clean up existing connection
      if (wsRef.current) {
        wsRef.current.close();
      }

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected:', url);
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttemptsRef.current = 0;
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('WebSocket message received:', message);
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
          console.error('Raw message data:', event.data);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;
        onDisconnect?.();

        // Auto-reconnect logic
        if (autoReconnect && event.code !== 1000) {
          const maxReconnectAttempts = 10;
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current++;
            console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, reconnectInterval);
          } else {
            setConnectionError('Maximum reconnection attempts reached');
          }
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionError('Connection failed');
        onError?.(error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionError('Failed to create connection');
    }
  }, [url, onMessage, onConnect, onDisconnect, onError, autoReconnect, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Intentional disconnect');
      wsRef.current = null;
    }
    
    setIsConnected(false);
    reconnectAttemptsRef.current = 0;
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
        return false;
      }
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', message);
      return false;
    }
  }, []);

  // Initialize connection on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    connectionError,
    connect,
    disconnect,
    sendMessage,
  };
};
