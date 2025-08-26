import { useState, useEffect, useRef, useCallback } from 'react';

export interface TerminalMessage {
  type: 'terminal_connected' | 'terminal_start' | 'terminal_output' | 'terminal_end';
  session_id?: string;
  stream?: 'stdout' | 'stderr';
  output?: string;
  timestamp?: number;
  message?: string;
  command?: string;
  cwd?: string;
  is_error?: boolean;
  completed?: boolean;
  exit_code?: number;
  duration?: number;
}

export interface LogEntry {
  id: number;
  timestamp: string;
  type: 'info' | 'success' | 'error' | 'warning' | 'command' | 'output';
  message: string;
  stage?: string;
  isTyping?: boolean;
  stream?: 'stdout' | 'stderr';
}

interface UseTerminalWebSocketOptions {
  url: string;
  onMessage?: (message: TerminalMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: string) => void;
  autoReconnect?: boolean;
}

export const useTerminalWebSocket = (options: UseTerminalWebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [logId, setLogId] = useState(0);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 3; // Match pipeline WebSocket
  const hasReachedMaxAttemptsRef = useRef(false);
  const connectionInitializedRef = useRef(false); // Match pipeline WebSocket pattern

  const addLog = useCallback((newLog: Omit<LogEntry, 'id'>) => {
    setLogs(prev => {
      const logWithId = {
        ...newLog,
        id: prev.length > 0 ? Math.max(...prev.map(l => l.id)) + 1 : 0
      };
      // Keep last 100 logs to prevent memory issues
      return [...prev.slice(-99), logWithId];
    });
  }, []);

  const connect = useCallback(() => {
    // Don't create multiple connections
    if (ws.current && ws.current.readyState === WebSocket.CONNECTING) {
      console.log('⏳ Terminal WebSocket connection already in progress');
      return;
    }

    try {
      // Clean up existing connection
      if (ws.current) {
        ws.current.close();
      }

      console.log(`🔌 Attempting Terminal WebSocket connection to: ${options.url}`);
      ws.current = new WebSocket(options.url);

      ws.current.onopen = () => {
        console.log('✅ Terminal WebSocket connected successfully!');
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttempts.current = 0;
        hasReachedMaxAttemptsRef.current = false;
        
        // Add connection log
        addLog({
          timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
          type: 'success',
          message: '🔌 Terminal WebSocket connected - Ready for real-time output',
        });

        options.onConnect?.();
      };

      ws.current.onmessage = (event) => {
        try {
          const message: TerminalMessage = JSON.parse(event.data);
          console.log('📊 Terminal WebSocket message:', message);

          // Handle different message types
          switch (message.type) {
            case 'terminal_connected':
              addLog({
                timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
                type: 'info',
                message: `📡 ${message.message || 'Terminal session connected'}`,
              });
              break;

            case 'terminal_start':
              addLog({
                timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
                type: 'command',
                message: `PS ${message.cwd || 'C:\\'}> ${message.command || ''}`,
              });
              break;

            case 'terminal_output':
              if (message.output) {
                // Split output by lines and add each line as a separate log entry
                const lines = message.output.split('\n');
                lines.forEach((line, index) => {
                  // Skip empty lines except the last one (for spacing)
                  if (line.trim() || index === lines.length - 1) {
                    addLog({
                      timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
                      type: message.is_error ? 'error' : 'output',
                      message: line,
                      stream: message.stream,
                    });
                  }
                });
              }
              break;

            case 'terminal_end':
              const exitMessage = message.exit_code === 0 
                ? `✅ Command completed successfully (${message.duration?.toFixed(1)}s)`
                : `❌ Command failed with exit code ${message.exit_code} (${message.duration?.toFixed(1)}s)`;
              
              addLog({
                timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
                type: message.exit_code === 0 ? 'success' : 'error',
                message: exitMessage,
              });
              break;

            default:
              console.log('🔄 Unknown terminal message type:', message.type);
          }

          options.onMessage?.(message);
        } catch (error) {
          console.error('❌ Failed to parse terminal WebSocket message:', error);
          addLog({
            timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
            type: 'error',
            message: `❌ Failed to parse message: ${error}`,
          });
        }
      };

      ws.current.onclose = (event) => {
        console.log(`🔌 Terminal WebSocket disconnected: Code ${event.code}, Reason: ${event.reason}`);
        setIsConnected(false);
        ws.current = null;
        
        addLog({
          timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
          type: 'warning',
          message: `⚠️ Terminal WebSocket disconnected (${event.code}: ${event.reason || 'Connection closed'})`,
        });

        options.onDisconnect?.();

        // Only auto-reconnect if enabled, not intentionally closed, and haven't reached max attempts
        if (options.autoReconnect && event.code !== 1000 && !hasReachedMaxAttemptsRef.current) {
          if (reconnectAttempts.current < maxReconnectAttempts) {
            reconnectAttempts.current++;
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current - 1), 30000);
            console.log(`🔄 Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts}) in ${delay}ms...`);
            
            addLog({
              timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
              type: 'info',
              message: `🔄 Reconnecting in ${delay/1000}s... (${reconnectAttempts.current}/${maxReconnectAttempts})`,
            });
            
            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, delay);
          } else {
            console.log('❌ Maximum reconnection attempts reached. Stopping reconnection.');
            hasReachedMaxAttemptsRef.current = true;
            setConnectionError('Maximum reconnection attempts reached');
            addLog({
              timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
              type: 'error',
              message: '❌ Maximum reconnection attempts reached. Connection stopped.',
            });
          }
        }
      };

      ws.current.onerror = (error) => {
        console.error('❌ Terminal WebSocket error:', error);
        if (!isConnected) {
          setConnectionError('Connection failed');
        }
        
        addLog({
          timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
          type: 'error',
          message: `❌ WebSocket error: Connection failed`,
        });

        options.onError?.('Connection failed');
      };

    } catch (error) {
      console.error('❌ Failed to create Terminal WebSocket connection:', error);
      setConnectionError('Failed to create connection');
      hasReachedMaxAttemptsRef.current = true;
    }
  }, [options.url, options.onConnect, options.onDisconnect, options.onError, options.autoReconnect, isConnected, addLog]);

  const disconnect = useCallback(() => {
    console.log('🔌 Intentionally disconnecting Terminal WebSocket');
    
    // Clear any pending reconnection attempts
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    // Close the WebSocket connection
    if (ws.current) {
      ws.current.close(1000, 'Intentional disconnect');
      ws.current = null;
    }
    
    // Reset state
    setIsConnected(false);
    setConnectionError(null);
    reconnectAttempts.current = 0;
    hasReachedMaxAttemptsRef.current = false;
  }, []);

  const clearLogs = useCallback(() => {
    setLogs([]);
    setLogId(0);
  }, []);

  // Initialize connection ONLY ONCE per component mount (session)
  useEffect(() => {
    if (!connectionInitializedRef.current) {
      console.log('🚀 Initializing Terminal WebSocket connection for new session');
      connectionInitializedRef.current = true;
      
      // Add initial system messages
      const initLogs: LogEntry[] = [
        {
          id: 0,
          timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
          type: 'output',
          message: 'Windows PowerShell - Hackademia Pipeline',
        },
        {
          id: 1,
          timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
          type: 'output',
          message: 'Copyright (C) Microsoft Corporation. All rights reserved.',
        },
        {
          id: 2,
          timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
          type: 'output',
          message: '',
        }
      ];
      
      setLogs(initLogs);
      setLogId(3);
      
      // Small delay to avoid rapid connection attempts
      const timer = setTimeout(() => {
        connect();
      }, 100);

      return () => {
        clearTimeout(timer);
      };
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log('🧹 Cleaning up Terminal WebSocket on component unmount');
      disconnect();
    };
  }, [disconnect]);

  // Reset max attempts flag when URL changes
  useEffect(() => {
    console.log('🔄 Terminal WebSocket URL changed, resetting connection attempts');
    hasReachedMaxAttemptsRef.current = false;
    reconnectAttempts.current = 0;
    connectionInitializedRef.current = false;
  }, [options.url]);

  return {
    isConnected,
    connectionError,
    logs,
    clearLogs,
    connect,
    disconnect,
  };
};
