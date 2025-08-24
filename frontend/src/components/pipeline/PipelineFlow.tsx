import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause } from 'lucide-react';
import { StageCard } from './StageCard';
import { SummaryCard } from './SummaryCard';
import { Terminal } from './Terminal';
import { StagePopup } from './StagePopup';
import { FlowConnections } from './FlowConnections';
import { useWebSocket, type WebSocketMessage } from '../../hooks/useWebSocket';

export type StageStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'success' | 'skipped';

export interface Stage {
  id: string;
  name: string;
  description: string;
  icon: string;
  status: StageStatus;
  agent: string;
  progress?: number;
  duration?: number;
  details: {
    action: string;
    example: string;
    logs?: string[];
  };
  // WebSocket data from backend
  results?: {
    // Common properties
    files_analyzed?: number;
    // Build stage specific results
    build_logs?: string[];
    errors?: string[];
    dependencies_found?: number;
    project_type?: string;
    // Analyze stage specific results
    total_issues?: number;
    vulnerabilities?: Array<{
      type: string;
      severity: string;
      file: string;
      line: number;
      description: string;
      cwe_id?: string;
      confidence: number;
    }>;
    security_issues?: Array<{
      type: string;
      severity: string;
      file: string;
      line: number;
      description: string;
      confidence: number;
    }>;
    quality_issues?: Array<{
      type: string;
      severity: string;
      file: string;
      line: number;
      description: string;
      confidence: number;
    }>;
    recommendations?: string[];
    // Test stage results
    total_tests?: number;
    passed_tests?: number;
    failed_tests?: number;
    coverage?: number;
    test_logs?: string[];
    test_failures?: Array<{
      test_name: string;
      error_message: string;
      file: string;
      line: number;
    }>;
    // Fix stage results  
    fixes_applied?: number;
    issues_resolved?: Array<{
      type: string;
      file: string;
      line: number;
      description: string;
      fix_applied: string;
      confidence: number;
    }>;
    remaining_issues?: number;
    fix_logs?: string[];
    // Results stage results
    overall_status?: 'success' | 'partial' | 'failed';
    summary?: {
      total_issues_found: number;
      issues_fixed: number;
      tests_passed: number;
      coverage_improvement: number;
    };
    metadata?: {
      mcp_questions_asked?: number;
      context_gathered?: string;
      analysis_time?: number;
      ai_model?: string;
      overall_risk_level?: string;
      confidence_scores?: {
        overall: number;
        vulnerability_detection: number;
        false_positive_rate: number;
      };
    };
  };
}

const initialStages: Stage[] = [
  {
    id: 'pr',
    name: 'PR Creation',
    description: 'New pull request submitted',
    icon: '📝',
    status: 'completed',
    agent: 'PR',
    details: {
      action: 'A developer submits a pull request with new code changes',
      example: 'PR #247: "Add user authentication feature" submitted by @john_dev',
      logs: ['PR created successfully', 'Branch validation passed', 'Ready for pipeline']
    }
  },
  {
    id: 'build',
    name: 'Build & Compile',
    description: 'Building and compiling code',
    icon: '🔨',
    status: 'completed',
    agent: 'BD',
    details: {
      action: 'The Build Agent compiles your code and checks for basic errors',
      example: 'Compiled 847 files, generated optimized bundles (2.3MB → 890KB)',
      logs: ['Installing dependencies...', 'Compiling TypeScript...', 'Build completed successfully']
    }
  },
  {
    id: 'analyze',
    name: 'AI Analysis',
    description: 'Analyzing code for issues',
    icon: '🧠',
    status: 'in_progress',
    agent: 'AI',
    details: {
      action: 'Gemini AI analyzes your code for bugs, security issues, and best practices',
      example: 'Found 3 potential security vulnerabilities and 7 code quality improvements',
      logs: ['Scanning for security vulnerabilities...', 'Checking code quality...', 'Running AI analysis...']
    }
  },
  {
    id: 'fix',
    name: 'Auto Fix',
    description: 'Automatically fixing detected issues',
    icon: '🔧',
    status: 'pending',
    agent: 'FX',
    details: {
      action: 'The Fix Agent automatically resolves issues found during analysis',
      example: 'Fixed SQL injection vulnerability, optimized 4 database queries',
      logs: []
    }
  },
  {
    id: 'test',
    name: 'Testing',
    description: 'Running comprehensive tests',
    icon: '✅',
    status: 'pending',
    agent: 'QA',
    details: {
      action: 'Runs unit tests, integration tests, and validates the fixes work correctly',
      example: 'Executed 234 tests, 98.5% coverage, all critical paths validated',
      logs: []
    }
  },
  {
    id: 'results',
    name: 'Results',
    description: 'Pipeline complete with summary',
    icon: '📊',
    status: 'pending',
    agent: 'RP',
    details: {
      action: 'Provides a comprehensive report of all changes and improvements made',
      example: 'Pipeline successful! 10 issues fixed, tests pass, ready to merge',
      logs: []
    }
  }
];

export const PipelineFlow: React.FC = () => {
  const [stages, setStages] = useState<Stage[]>(initialStages);
  const [currentStage, setCurrentStage] = useState('pr');
  const [activeStageIndex, setActiveStageIndex] = useState(0);
  const [showPopup, setShowPopup] = useState(false);
  const [popupPosition, setPopupPosition] = useState({ x: 0, y: 0 });
  const [stagePositions, setStagePositions] = useState<Array<{ x: number; y: number; width: number; height: number }>>([]);
  const [autoFocusStage, setAutoFocusStage] = useState(0); // Auto focus always active
  const [clickedStage, setClickedStage] = useState<Stage | null>(null); // New: track clicked stage
  const [isPaused, setIsPaused] = useState(false); // Play/Pause state
  const [shouldResumeFrom, setShouldResumeFrom] = useState<number | null>(null); // Resume point
  const stageRefs = useRef<Array<HTMLDivElement | null>>([]);
  const automationTimeoutRef = useRef<NodeJS.Timeout | null>(null); // Track automation timeout
  const [pipelineId, setPipelineId] = useState<string>('demo-pipeline-' + Date.now());
  const [isRealTimeMode, setIsRealTimeMode] = useState(false);

  // WebSocket connection for real-time data
  const handleWebSocketMessage = (message: WebSocketMessage) => {
    console.log('Received WebSocket message:', message);
    
    switch (message.type) {
      case 'pipeline_start':
        console.log('Pipeline started:', message.pipeline_id);
        setIsRealTimeMode(true);
        // Reset stages to initial state for real pipeline
        setStages(initialStages.map(stage => ({ ...stage, status: 'pending', results: undefined })));
        break;
        
      case 'stage_start':
        if (message.stage) {
          console.log('Stage started:', message.stage);
          setStages(prevStages => prevStages.map(stage => 
            stage.id === message.stage ? { ...stage, status: 'in_progress' } : stage
          ));
          // Focus on started stage
          const stageIndex = initialStages.findIndex(s => s.id === message.stage);
          if (stageIndex !== -1) {
            setActiveStageIndex(stageIndex);
            setAutoFocusStage(stageIndex);
            setCurrentStage(message.stage);
            showAutoFocusPopup(stageIndex);
          }
        }
        break;
        
      case 'status_update':
        if (message.stage && message.data) {
          console.log('Status update for stage:', message.stage, message.data);
          setStages(prevStages => prevStages.map(stage => 
            stage.id === message.stage ? { 
              ...stage, 
              status: message.status || stage.status,
              // Update logs with new data
              details: {
                ...stage.details,
                logs: message.data.logs ? [...(stage.details.logs || []), ...message.data.logs] : stage.details.logs
              }
            } : stage
          ));
        }
        break;
        
      case 'stage_complete':
        if (message.stage && message.results) {
          console.log('Stage completed:', message.stage, message.results);
          setStages(prevStages => prevStages.map(stage => 
            stage.id === message.stage ? { 
              ...stage, 
              status: 'completed',
              results: message.results
            } : stage
          ));
        }
        break;
        
      case 'pipeline_complete':
        console.log('Pipeline completed:', message.pipeline_id);
        setIsRealTimeMode(false);
        setShowPopup(false);
        // Maybe show a completion notification
        break;
    }
  };

  const { isConnected, connectionError } = useWebSocket({
    url: `ws://localhost:8000/ws/${pipelineId}`,
    onMessage: handleWebSocketMessage,
    onConnect: () => {
      console.log('Connected to WebSocket');
    },
    onDisconnect: () => {
      console.log('Disconnected from WebSocket');
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    },
    autoReconnect: true,
  });

  // Function to show auto-focus popup (only when not paused and no manual click)
  const showAutoFocusPopup = (stageIndex: number) => {
    // Don't show auto-focus popup if paused or if user manually clicked a stage
    if (isPaused || clickedStage) return;
    
    const stageRef = stageRefs.current[stageIndex];
    if (stageRef) {
      const rect = stageRef.getBoundingClientRect();
      const container = stageRef.closest('.pipeline-container')?.getBoundingClientRect();
      
      // Smart popup positioning - left side for later stages
      const isRightSideStage = stageIndex >= 3;
      
      if (isRightSideStage) {
        setPopupPosition({
          x: rect.left - (container?.left || 0) - 570,
          y: rect.top - (container?.top || 0) + (rect.height / 2) - 190
        });
      } else {
        setPopupPosition({
          x: rect.right - (container?.left || 0) + 70,
          y: rect.top - (container?.top || 0) + (rect.height / 2) - 190
        });
      }
      
      // Clear clicked stage to show auto-focus popup
      setClickedStage(null);
      setShowPopup(true);
    }
  };

  // Demo mode pipeline automation with auto-focus (only when not receiving real data)
  useEffect(() => {
    // Don't run demo mode if we're in real-time mode or connected to backend
    if (isRealTimeMode || isConnected) {
      return;
    }

    const automateStages = async () => {
      // Start from resume point or beginning
      const startIndex = shouldResumeFrom !== null ? shouldResumeFrom : 0;
      setShouldResumeFrom(null);
      
      for (let i = startIndex; i < stages.length; i++) {
        // Check again in case real-time mode started during loop or paused
        if (isRealTimeMode || isPaused) break;
        
        // Set current stage as active with auto-focus
        setActiveStageIndex(i);
        setAutoFocusStage(i);
        setCurrentStage(stages[i].id);
        
        // Update stage status to progress
        setStages(prevStages => prevStages.map((stage, index) => 
          index === i ? { ...stage, status: 'in_progress' as StageStatus } : stage
        ));
        
        // Use the helper function for popup positioning
        showAutoFocusPopup(i);
        
        // Simulate stage processing time with auto-focus
        const processingTime = Math.random() * 4000 + 3000; // 3-7 seconds for better viewing
        await new Promise(resolve => {
          automationTimeoutRef.current = setTimeout(() => {
            if (!isPaused && !isRealTimeMode) {
              resolve(undefined);
            }
          }, processingTime);
        });
        
        // Check again before completing in case real-time mode started or paused
        if (isRealTimeMode || isPaused) {
          setShouldResumeFrom(i); // Save current position for resume
          break;
        }
        
        // Complete current stage
        setStages(prevStages => prevStages.map((stage, index) => 
          index === i ? { ...stage, status: 'completed' as StageStatus } : stage
        ));
        
        setShowPopup(false);
        
        // Brief pause between stages
        await new Promise(resolve => {
          automationTimeoutRef.current = setTimeout(() => {
            if (!isPaused && !isRealTimeMode) {
              resolve(undefined);
            }
          }, 800);
        });
        
        if (isPaused || isRealTimeMode) {
          setShouldResumeFrom(i + 1); // Resume from next stage
          break;
        }
      }
      
      // Only continue demo loop if still not in real-time mode and not paused
      if (!isRealTimeMode && !isPaused && shouldResumeFrom === null) {
        // All stages completed - reset for continuous auto-focus demo
        setActiveStageIndex(stages.length);
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Reset and restart auto-focus cycle
        setStages(initialStages);
        setActiveStageIndex(0);
        setAutoFocusStage(0);
        automateStages(); // Continuous loop
      }
    };

    // Start auto-focus automation after initial render
    if (!isPaused) {
      const timer = setTimeout(() => {
        automateStages();
      }, 1000);
      automationTimeoutRef.current = timer;

      return () => {
        if (automationTimeoutRef.current) {
          clearTimeout(automationTimeoutRef.current);
        }
      };
    }
  }, [isRealTimeMode, isConnected, isPaused, shouldResumeFrom]);

  // Update stage positions for connections
  useEffect(() => {
    const updatePositions = () => {
      const positions = stageRefs.current.map(ref => {
        if (ref) {
          const rect = ref.getBoundingClientRect();
          const container = ref.closest('.pipeline-container')?.getBoundingClientRect();
          return {
            x: rect.left - (container?.left || 0),
            y: rect.top - (container?.top || 0),
            width: rect.width,
            height: rect.height
          };
        }
        return { x: 0, y: 0, width: 0, height: 0 };
      });
      setStagePositions(positions);
    };

    updatePositions();
    window.addEventListener('resize', updatePositions);
    return () => window.removeEventListener('resize', updatePositions);
  }, [activeStageIndex]);

  // Handle escape key to close popup when paused
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isPaused && showPopup) {
        handleClosePopup();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isPaused, showPopup]);

  const handleStageClick = (stage: Stage) => {
    setCurrentStage(stage.id); // Update current stage for terminal
    
    // If paused, give priority to manual click over auto-focus
    if (isPaused && !isRealTimeMode) {
      const stageIndex = stages.findIndex(s => s.id === stage.id);
      setActiveStageIndex(stageIndex);
      setAutoFocusStage(stageIndex);
      
      // Set clicked stage and force popup for the clicked stage
      setClickedStage(stage);
      
      // Clear any existing auto-focus popup first
      setShowPopup(false);
      
      // Position popup for the manually clicked stage
      const stageRef = stageRefs.current[stageIndex];
      if (stageRef) {
        const rect = stageRef.getBoundingClientRect();
        const container = stageRef.closest('.pipeline-container')?.getBoundingClientRect();
        
        // Smart popup positioning - left side for later stages
        const isRightSideStage = stageIndex >= 3;
        
        if (isRightSideStage) {
          setPopupPosition({
            x: rect.left - (container?.left || 0) - 570,
            y: rect.top - (container?.top || 0) + (rect.height / 2) - 190
          });
        } else {
          setPopupPosition({
            x: rect.right - (container?.left || 0) + 70,
            y: rect.top - (container?.top || 0) + (rect.height / 2) - 190
          });
        }
        
        // Small delay to ensure clean popup display
        setTimeout(() => {
          setShowPopup(true);
        }, 50);
      }
      return; // Exit early to avoid normal click handling
    }
    
    // Normal click handling for non-paused state
    setClickedStage(stage); // Set the clicked stage for popup
    
    // Position popup near the clicked stage
    const stageIndex = stages.findIndex(s => s.id === stage.id);
    const stageRef = stageRefs.current[stageIndex];
    
    if (stageRef) {
      const rect = stageRef.getBoundingClientRect();
      const container = stageRef.closest('.pipeline-container')?.getBoundingClientRect();
      
      // Smart popup positioning - left side for later stages
      const isRightSideStage = stageIndex >= 3; // Auto Fix, Testing, Results (indices 3, 4, 5)
      
      if (isRightSideStage) {
        // Position popup on LEFT side for right stages
        setPopupPosition({
          x: rect.left - (container?.left || 0) - 570,
          y: rect.top - (container?.top || 0) + (rect.height / 2) - 190
        });
      } else {
        // Position popup on RIGHT side for left stages
        setPopupPosition({
          x: rect.right - (container?.left || 0) + 70,
          y: rect.top - (container?.top || 0) + (rect.height / 2) - 190
        });
      }
      
      setShowPopup(true);
    }
  };

  // Play/Pause toggle function
  const togglePlayPause = () => {
    if (isRealTimeMode || isConnected) return; // Don't allow pause during real-time mode
    
    setIsPaused(!isPaused);
    
    if (isPaused) {
      // Resuming: clear manual click state to allow auto-focus to work
      setClickedStage(null);
      setShowPopup(false);
      
      if (shouldResumeFrom !== null) {
        // Resume animation from saved position
        setShouldResumeFrom(shouldResumeFrom);
      }
    }
  };

  // Handle closing popup when paused (allow user to close manually clicked popup)
  const handleClosePopup = () => {
    setShowPopup(false);
    setClickedStage(null);
  };

  const completedStages = stages.filter(stage => stage.status === 'completed').length;
  const progress = (completedStages / stages.length) * 100;

  const summaryData = {
    prStatus: 'In Progress',
    issuesFixed: 3,
    testCoverage: 98.5,
    mergeReadiness: activeStageIndex >= 4 ? 'Ready' : 'Not Ready'
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-full mx-auto p-6 overflow-x-visible">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative mb-6"
        >
          {/* Project Graph Button - Top Left */}
          <div className="absolute top-0 left-0">
            <motion.a
              href="https://app.codegpt.co/en/graph/ad112ff3-0fca-4576-a30c-adc501970b39"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-4 py-2 bg-purple-600/80 hover:bg-purple-700/90 text-white rounded-lg font-medium flex items-center gap-2 transition-all duration-200 backdrop-blur-sm border border-purple-500/30 shadow-lg"
            >
              🕸️ Project Graph
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </motion.a>
          </div>

          {/* WebSocket Connection Status - Top Right */}
          <div className="absolute top-0 right-0">
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${
              isConnected 
                ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                : connectionError 
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                  : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-400' : connectionError ? 'bg-red-400' : 'bg-yellow-400'
              }`} />
              {isConnected 
                ? `Connected (${isRealTimeMode ? 'Real-time' : 'Demo Mode'})`
                : connectionError 
                  ? `Disconnected - ${connectionError}`
                  : 'Connecting...'
              }
            </div>
          </div>
          
          {/* Centered Title and Description */}
          <div className="text-center">
            <h1 className="text-3xl font-bold mb-3 bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              DevOps CI/CD Pipeline
            </h1>
            <p className="text-muted-foreground text-base">
              AI-powered self-healing pipeline that fixes issues automatically
            </p>
            {/* Pause Indicator */}
            {isPaused && !isRealTimeMode && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-2 inline-flex items-center gap-2 px-3 py-1 bg-orange-500/20 text-orange-400 border border-orange-500/30 rounded-full text-sm font-medium"
              >
                <Pause className="w-4 h-4" />
                Pipeline Paused - Click stages to inspect or resume animation
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Main Layout - Split View */}
        <div className="flex gap-6" style={{ height: 'calc(100vh - 140px)' }}>
          {/* Left Side - Pipeline Content */}
          <div className="flex-1 flex flex-col gap-4 min-w-0 overflow-hidden">
            {/* Pipeline Summary - Compact version */}
            <div className="flex-shrink-0">
              <SummaryCard data={summaryData} />
            </div>

            {/* Pipeline Stages - Canvas-like container */}
            <div className="flex-1 relative pipeline-container overflow-hidden bg-black">
              {/* Flow Connections */}
              <FlowConnections 
                stages={stages}
                activeStageIndex={activeStageIndex}
                stagePositions={stagePositions}
              />
              
              {/* Pipeline Stages - Auto-focus in center of canvas */}
              <div className="relative h-full flex items-center justify-center">

                <div className="flex items-center gap-12 px-8 relative z-20">
                  {stages.map((stage, index) => (
                    <motion.div
                      key={stage.id}
                      ref={el => stageRefs.current[index] = el}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ 
                        opacity: 1, 
                        scale: index === activeStageIndex ? 1.3 : // Bigger scale for auto-focus
                               index === autoFocusStage ? 1.2 : 1,
                        x: (() => {
                          if (!showPopup) return 0;
                          
                          // Smart card pushing logic
                          const activeIndex = activeStageIndex;
                          
                          if (activeIndex <= 2) {
                            // For stages 0-2 (PR, Build, AI Analysis): push RIGHT side cards to right
                            return index > activeIndex ? 400 : 0; // More push for bigger popup
                          } else {
                            // For stages 3-5 (Auto Fix, Testing, Results): push LEFT side cards to left
                            return index < activeIndex ? -400 : 0; // More push for bigger popup
                          }
                        })(),
                        y: index === autoFocusStage ? -10 : 0, // Slight lift for focused stage
                        zIndex: index === autoFocusStage ? 30 : 20,
                        filter: index === autoFocusStage ? "brightness(1.2) saturate(1.3)" : "brightness(1)",
                        transition: {
                          duration: 0.8,
                          ease: "easeInOut",
                          scale: { duration: 0.5 },
                          x: { duration: 0.8, ease: "easeOut" },
                          y: { duration: 0.6 },
                          filter: { duration: 0.4 }
                        }
                      }}
                      transition={{ 
                        duration: 0.6, 
                        ease: "easeInOut",
                        delay: index * 0.1 
                      }}
                      className="flex-shrink-0 relative"
                      style={{ zIndex: index === autoFocusStage ? 30 : 20 }}
                    >
                      <StageCard
                        stage={stage}
                        isActive={index === activeStageIndex}
                        onClick={() => handleStageClick(stage)}
                        isCompact={true}
                      />
                    </motion.div>
                  ))}
                </div>
                
                {/* Dynamic Stage Popup with smart positioning */}
                <StagePopup
                  stage={clickedStage || stages[activeStageIndex]}
                  isVisible={showPopup}
                  position={popupPosition}
                  isLeftSide={activeStageIndex >= 3} // Left side for Auto Fix, Testing, Results
                  isClickedMode={clickedStage !== null}
                  onClose={handleClosePopup}
                />
              </div>
            </div>
          </div>

          {/* Right Sidebar - Terminal */}
          <div className="w-96 flex-shrink-0 flex flex-col" style={{ height: '100%' }}>
            {/* Terminal Header - Green box area */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-t-lg p-3 flex-shrink-0">
              <motion.h2
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="text-lg font-bold text-white flex items-center gap-2"
              >
                <span className="text-green-400"></span>
                Terminal
              </motion.h2>
            </div>
            
            {/* Terminal Container - Full height */}
            <div className="flex-1 min-h-0 h-full">
              <Terminal 
                isActive={true}
                currentStage={currentStage}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};