import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Maximize2, Minimize2, X, Copy, Settings } from 'lucide-react';

interface TerminalProps {
  isActive: boolean;
  currentStage: string;
}

interface LogEntry {
  id: number;
  timestamp: string;
  type: 'info' | 'success' | 'error' | 'warning' | 'command' | 'output';
  message: string;
  stage?: string;
  isTyping?: boolean;
}

export const Terminal: React.FC<TerminalProps> = ({ isActive, currentStage }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isMaximized, setIsMaximized] = useState(false);
  const [currentTypingLog, setCurrentTypingLog] = useState<LogEntry | null>(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const [logId, setLogId] = useState(0);

  // Simulate real-time backend logs with typing animation
  useEffect(() => {
    if (!isActive) return;

    const generateLog = (): LogEntry => {
      const now = new Date();
      const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
      
      const logMessages = {
        'pr': [
          { type: 'command' as const, message: 'git pull origin main' },
          { type: 'output' as const, message: 'Already up to date.' },
          { type: 'command' as const, message: 'git checkout -b feature/user-auth' },
          { type: 'output' as const, message: 'Switched to a new branch \'feature/user-auth\'' },
          { type: 'command' as const, message: 'git add .' },
          { type: 'command' as const, message: 'git commit -m "Add user authentication system"' },
          { type: 'output' as const, message: '[feature/user-auth 7f3a2b1] Add user authentication system' },
          { type: 'output' as const, message: ' 15 files changed, 847 insertions(+), 23 deletions(-)' },
          { type: 'success' as const, message: '✅ PR #247 created successfully' }
        ],
        'build': [
          { type: 'command' as const, message: 'npm ci' },
          { type: 'output' as const, message: 'npm WARN deprecated @types/eslint@8.4.10: This is a stub types definition' },
          { type: 'output' as const, message: 'added 847 packages in 23.456s' },
          { type: 'command' as const, message: 'npm run build' },
          { type: 'output' as const, message: '> hackademia-pipeline@1.0.0 build' },
          { type: 'output' as const, message: '> tsc && vite build' },
          { type: 'output' as const, message: 'vite v5.4.19 building for production...' },
          { type: 'output' as const, message: '✓ 156 modules transformed.' },
          { type: 'output' as const, message: 'dist/index.html                   0.46 kB │ gzip:  0.30 kB' },
          { type: 'success' as const, message: '✅ Build completed successfully' }
        ],
        'analyze': [
          { type: 'command' as const, message: 'python -m gemini_analyzer --scan ./src' },
          { type: 'output' as const, message: 'Gemini AI Analysis Engine v2.1.0' },
          { type: 'output' as const, message: 'Scanning directory: ./src' },
          { type: 'output' as const, message: 'Found 47 TypeScript files, 23 Python files' },
          { type: 'warning' as const, message: '⚠️  [SECURITY] Potential SQL injection in user.controller.js:42' },
          { type: 'error' as const, message: '🚨 [CRITICAL] Hardcoded API key detected in config.ts:15' },
          { type: 'warning' as const, message: '⚠️  [PERFORMANCE] Inefficient database query in auth.service.ts:89' },
          { type: 'output' as const, message: 'Analysis complete: 3 vulnerabilities found' }
        ],
        'fix': [
          { type: 'command' as const, message: 'python -m fix_agent --apply-security-patches' },
          { type: 'output' as const, message: 'Auto-Fix Agent v3.2.1 initialized' },
          { type: 'output' as const, message: 'Applying security patches...' },
          { type: 'success' as const, message: '✅ Fixed SQL injection vulnerability in user.controller.js' },
          { type: 'success' as const, message: '✅ Moved API key to environment variables' },
          { type: 'command' as const, message: 'python -m optimize_db_queries' },
          { type: 'output' as const, message: 'Optimizing database queries...' },
          { type: 'success' as const, message: '✅ Query performance improved by 78%' }
        ],
        'test': [
          { type: 'command' as const, message: 'npm test -- --coverage --verbose' },
          { type: 'output' as const, message: 'Jest v29.7.0' },
          { type: 'output' as const, message: 'PASS  src/auth/auth.test.ts' },
          { type: 'output' as const, message: 'PASS  src/database/db.test.ts' },
          { type: 'error' as const, message: 'FAIL  src/api/user.test.ts' },
          { type: 'output' as const, message: '  ● UserController › should validate email format' },
          { type: 'output' as const, message: '    Expected: true, Received: false' },
          { type: 'success' as const, message: '✅ Test suite completed: 231/234 tests passed' },
          { type: 'output' as const, message: 'Coverage: 98.5% of statements' }
        ],
        'results': [
          { type: 'command' as const, message: 'python -m generate_report --pipeline-summary' },
          { type: 'output' as const, message: 'Generating pipeline execution report...' },
          { type: 'success' as const, message: '🎉 Pipeline execution completed successfully!' },
          { type: 'output' as const, message: 'Total issues fixed: 8/10' },
          { type: 'output' as const, message: 'Test coverage: 98.5%' },
          { type: 'success' as const, message: '✅ PR ready for review and merge' }
        ]
      };

      const stageMessages = logMessages[currentStage as keyof typeof logMessages] || logMessages['analyze'];
      const randomMessage = stageMessages[Math.floor(Math.random() * stageMessages.length)];

      return {
        id: logId,
        timestamp,
        type: randomMessage.type,
        message: randomMessage.message,
        stage: currentStage,
        isTyping: randomMessage.type === 'command' || Math.random() < 0.3 // Some outputs also type
      };
    };

    // Add initial system message
    if (logs.length === 0) {
      setLogs([{
        id: 0,
        timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
        type: 'output',
        message: 'Windows PowerShell',
      }, {
        id: 1,
        timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
        type: 'output',
        message: 'Copyright (C) Microsoft Corporation. All rights reserved.',
      }, {
        id: 2,
        timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
        type: 'output',
        message: '',
      }]);
      setLogId(3);
    }

    const addLogWithTyping = (newLog: LogEntry) => {
      if (newLog.isTyping && newLog.type === 'command') {
        // Add empty command line first
        const commandPrompt: LogEntry = {
          ...newLog,
          message: '',
          isTyping: true
        };
        setCurrentTypingLog(commandPrompt);
        setLogs(prev => [...prev.slice(-47), commandPrompt]); // Keep last 47 logs + typing
        
        // Type the command character by character
        let currentText = '';
        const fullText = newLog.message;
        let i = 0;
        
        const typeInterval = setInterval(() => {
          if (i < fullText.length) {
            currentText += fullText[i];
            setLogs(prev => {
              const updated = [...prev];
              const lastIndex = updated.length - 1;
              if (updated[lastIndex]?.id === commandPrompt.id) {
                updated[lastIndex] = {
                  ...commandPrompt,
                  message: currentText
                };
              }
              return updated;
            });
            i++;
          } else {
            // Typing complete
            clearInterval(typeInterval);
            setCurrentTypingLog(null);
            setTimeout(() => {
              setLogs(prev => {
                const updated = [...prev];
                const lastIndex = updated.length - 1;
                if (updated[lastIndex]?.id === commandPrompt.id) {
                  updated[lastIndex] = {
                    ...commandPrompt,
                    isTyping: false
                  };
                }
                return updated;
              });
            }, 200);
          }
        }, 50 + Math.random() * 100); // Realistic typing speed
      } else {
        setLogs(prev => [...prev.slice(-50), newLog]); // Keep last 50 logs
      }
      setLogId(prev => prev + 1);
    };

    const interval = setInterval(() => {
      const newLog = generateLog();
      addLogWithTyping(newLog);
    }, Math.random() * 3000 + 2000); // Random interval 2-5 seconds

    return () => clearInterval(interval);
  }, [isActive, currentStage, logId, logs.length]);

  // Auto scroll to bottom
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const getLogColor = (type: string) => {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      case 'command': return 'text-white';
      case 'output': return 'text-gray-300';
      default: return 'text-gray-300';
    }
  };

  const copyTerminalContent = () => {
    const content = logs.map(log => `[${log.timestamp}] ${log.message}`).join('\n');
    navigator.clipboard.writeText(content);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="bg-black rounded-b-lg border border-t-0 border-gray-600 overflow-hidden shadow-2xl font-['Consolas','Courier_New',monospace] h-full flex flex-col"
    >
      {/* Terminal Header - Windows Terminal Style */}
      <div className="bg-gray-800 px-4 py-2 flex items-center justify-between border-b border-gray-600 flex-shrink-0">
        <div className="flex items-center gap-3">
          {/* Windows Terminal Icon */}
          <div className="w-5 h-5 bg-blue-500 rounded-sm flex items-center justify-center">
            <span className="text-white text-xs font-bold">{'>'}</span>
          </div>
          <span className="text-gray-200 text-sm font-medium">
            Windows PowerShell - Hackademia Pipeline
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={copyTerminalContent}
            className="p-1.5 hover:bg-gray-700 rounded transition-colors"
            title="Copy terminal content"
          >
            <Copy className="w-4 h-4 text-gray-300" />
          </button>
          <button
            onClick={() => setIsMaximized(!isMaximized)}
            className="p-1.5 hover:bg-gray-700 rounded transition-colors"
          >
            {isMaximized ? (
              <Minimize2 className="w-4 h-4 text-gray-300" />
            ) : (
              <Maximize2 className="w-4 h-4 text-gray-300" />
            )}
          </button>
        </div>
      </div>

      {/* Terminal Content */}
      <div
        ref={terminalRef}
        className="p-4 font-mono text-sm bg-black flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent min-h-0"
      >
        {logs.map((log, index) => (
          <motion.div
            key={log.id}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.1 }}
            className="mb-1"
          >
            {log.type === 'command' ? (
              <div className="flex items-start">
                <span className="text-blue-400 mr-2 shrink-0">
                  PS C:\hackademia-pipeline{'>'} 
                </span>
                <span className={`${getLogColor(log.type)} leading-relaxed`}>
                  {log.message}
                  {log.isTyping && (
                    <motion.span
                      animate={{ opacity: [1, 0] }}
                      transition={{ repeat: Infinity, duration: 0.8 }}
                      className="bg-white w-2 h-4 inline-block ml-1"
                    />
                  )}
                </span>
              </div>
            ) : (
              <div className={`${getLogColor(log.type)} leading-relaxed pl-0`}>
                {log.message}
              </div>
            )}
          </motion.div>
        ))}
        
        {/* Active command prompt */}
        <motion.div
          animate={{ opacity: [1, 0.7] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          className="flex items-center mt-2"
        >
          <span className="text-blue-400 mr-2">
            PS C:\hackademia-pipeline{'>'} 
          </span>
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ repeat: Infinity, duration: 1 }}
            className="bg-white w-2 h-4 inline-block"
          />
        </motion.div>
      </div>
    </motion.div>
  );
};
