import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Bot, Zap, Clock } from 'lucide-react';
import { Stage } from './PipelineFlow';

interface AgentModalProps {
  stage: Stage | null;
  isOpen: boolean;
  onClose: () => void;
}

export const AgentModal: React.FC<AgentModalProps> = ({ stage, isOpen, onClose }) => {
  if (!stage) return null;

  const getAgentColor = (id: string) => {
    switch (id) {
      case 'pr': return 'text-blue-400';
      case 'build': return 'text-blue-400';
      case 'analyze': return 'text-purple-400';
      case 'fix': return 'text-orange-400';
      case 'test': return 'text-green-400';
      case 'results': return 'text-cyan-400';
      default: return 'text-muted-foreground';
    }
  };

  const getAgentBg = (id: string) => {
    switch (id) {
      case 'pr': return 'bg-blue-500/10';
      case 'build': return 'bg-blue-500/10';
      case 'analyze': return 'bg-purple-500/10';
      case 'fix': return 'bg-orange-500/10';
      case 'test': return 'bg-green-500/10';
      case 'results': return 'bg-cyan-500/10';
      default: return 'bg-muted/10';
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            onClick={onClose}
          />

          {/* Modal - Perfect center positioning */}
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="w-full max-w-2xl max-h-[85vh]"
            >
              <div className="bg-card/95 backdrop-blur-xl rounded-2xl shadow-2xl overflow-hidden border border-border/50">
                {/* Header */}
                <div className="bg-muted/20 backdrop-blur-sm p-6 border-b border-border/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="text-4xl">{stage.icon}</div>
                      <div>
                        <h2 className="text-2xl font-bold text-foreground">{stage.name}</h2>
                        <p className="text-primary font-medium flex items-center gap-2">
                          <Bot className="w-4 h-4" />
                          {stage.agent} Agent
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={onClose}
                      className="p-2 hover:bg-muted/50 rounded-full transition-colors"
                    >
                      <X className="w-5 h-5 text-muted-foreground hover:text-foreground" />
                    </button>
                  </div>
                </div>

                {/* Content - Scrollable */}
                <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(85vh-120px)] scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent">
                  {/* Build Stage - Real Data */}
                  {stage.id === 'build' && stage.results ? (
                    <>
                      <div>
                        <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                          <Zap className="w-5 h-5 text-blue-400" />
                          Build Status
                        </h3>
                        <div className="bg-muted/20 border border-muted/30 rounded-lg p-4">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            {stage.results.files_analyzed && (
                              <div>
                                <span className="text-muted-foreground">Files Analyzed:</span>
                                <span className="text-foreground font-medium ml-2">{stage.results.files_analyzed}</span>
                              </div>
                            )}
                            {stage.results.dependencies_found && (
                              <div>
                                <span className="text-muted-foreground">Dependencies:</span>
                                <span className="text-foreground font-medium ml-2">{stage.results.dependencies_found}</span>
                              </div>
                            )}
                            {stage.results.project_type && (
                              <div className="col-span-2">
                                <span className="text-muted-foreground">Project Type:</span>
                                <span className="text-foreground font-medium ml-2">{stage.results.project_type}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      {stage.results.build_logs && stage.results.build_logs.length > 0 && (
                        <div>
                          <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-green-400" />
                            Build Logs
                          </h3>
                          <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4 font-mono text-sm max-h-40 overflow-y-auto">
                            {stage.results.build_logs.map((log, index) => (
                              <div key={index} className="text-green-400 mb-1">
                                <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span> {log}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : stage.id === 'analyze' && stage.results ? (
                    <>
                      <div>
                        <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                          <Zap className="w-5 h-5 text-purple-400" />
                          Analysis Results
                        </h3>
                        <div className="bg-muted/20 border border-muted/30 rounded-lg p-4">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            {stage.results.files_analyzed && (
                              <div>
                                <span className="text-muted-foreground">Files Analyzed:</span>
                                <span className="text-foreground font-medium ml-2">{stage.results.files_analyzed}</span>
                              </div>
                            )}
                            {stage.results.total_issues && (
                              <div>
                                <span className="text-muted-foreground">Total Issues:</span>
                                <span className="text-foreground font-medium ml-2">{stage.results.total_issues}</span>
                              </div>
                            )}
                            {stage.results.metadata?.overall_risk_level && (
                              <div className="col-span-2">
                                <span className="text-muted-foreground">Risk Level:</span>
                                <span className={`font-medium ml-2 ${
                                  stage.results.metadata.overall_risk_level === 'HIGH' ? 'text-red-400' :
                                  stage.results.metadata.overall_risk_level === 'MEDIUM' ? 'text-yellow-400' :
                                  'text-green-400'
                                }`}>
                                  {stage.results.metadata.overall_risk_level}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      {stage.results.vulnerabilities && stage.results.vulnerabilities.length > 0 && (
                        <div>
                          <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-red-400" />
                            Vulnerabilities ({stage.results.vulnerabilities.length})
                          </h3>
                          <div className="space-y-3 max-h-48 overflow-y-auto">
                            {stage.results.vulnerabilities.slice(0, 5).map((vuln, index) => (
                              <div key={index} className="bg-red-900/20 border border-red-700/50 rounded-lg p-3">
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-sm font-medium text-red-400">{vuln.type}</span>
                                  <span className={`text-xs px-2 py-1 rounded-full ${
                                    vuln.severity === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                                    vuln.severity === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                                    'bg-blue-500/20 text-blue-400'
                                  }`}>
                                    {vuln.severity}
                                  </span>
                                </div>
                                <p className="text-sm text-muted-foreground mb-2">{vuln.description}</p>
                                <div className="text-xs text-muted-foreground">
                                  {vuln.file}:{vuln.line} • Confidence: {Math.round(vuln.confidence * 100)}%
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : stage.id === 'test' && stage.results ? (
                    <>
                      <div>
                        <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                          <Zap className="w-5 h-5 text-green-400" />
                          Test Results
                        </h3>
                        <div className="bg-muted/20 border border-muted/30 rounded-lg p-4">
                          <div className="grid grid-cols-2 gap-4 text-center">
                            <div>
                              <div className="text-2xl font-bold text-green-400">{stage.results.passed_tests || 0}</div>
                              <div className="text-xs text-muted-foreground">Tests Passed</div>
                            </div>
                            <div>
                              <div className="text-2xl font-bold text-red-400">{stage.results.failed_tests || 0}</div>
                              <div className="text-xs text-muted-foreground">Tests Failed</div>
                            </div>
                          </div>
                          {stage.results.coverage && (
                            <div className="mt-4">
                              <div className="flex justify-between text-sm mb-2">
                                <span className="text-muted-foreground">Coverage</span>
                                <span className="text-foreground font-medium">{stage.results.coverage}%</span>
                              </div>
                              <div className="w-full bg-muted/30 rounded-full h-2">
                                <div className="bg-green-400 h-2 rounded-full" style={{width: `${stage.results.coverage}%`}}></div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {stage.results.test_failures && stage.results.test_failures.length > 0 && (
                        <div>
                          <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-red-400" />
                            Test Failures
                          </h3>
                          <div className="space-y-3 max-h-32 overflow-y-auto">
                            {stage.results.test_failures.map((failure, index) => (
                              <div key={index} className="bg-red-900/20 border border-red-700/50 rounded-lg p-3">
                                <div className="text-sm font-medium text-red-400 mb-1">{failure.test_name}</div>
                                <p className="text-sm text-muted-foreground">{failure.error_message}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : stage.id === 'test' ? (
                    <>
                      {/* Fallback for test stage without real data */}
                      <div>
                        <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                          <Zap className="w-5 h-5 text-orange-400" />
                          What this agent does
                        </h3>
                        <p className="text-muted-foreground leading-relaxed">{stage.details.action}</p>
                      </div>

                      {/* Unit Test Cases - Demo Data */}
                      <div>
                        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
                          <Clock className="w-5 h-5 text-green-400" />
                          Unit Test Cases (Demo)
                        </h3>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between p-3 bg-muted/20 border border-muted/30 rounded-lg backdrop-blur-sm">
                            <div className="flex items-center gap-3">
                              <div className="w-2 h-2 rounded-full bg-green-400"></div>
                              <span className="text-sm font-medium text-foreground">Authentication Module</span>
                            </div>
                            <span className="text-xs px-3 py-1 bg-green-500/20 border border-green-500/30 text-green-400 rounded-full">
                              45/45 PASS
                            </span>
                          </div>
                          
                          <div className="flex items-center justify-between p-3 bg-muted/20 border border-muted/30 rounded-lg backdrop-blur-sm">
                            <div className="flex items-center gap-3">
                              <div className="w-2 h-2 rounded-full bg-red-400"></div>
                              <span className="text-sm font-medium text-foreground">Database Queries</span>
                            </div>
                            <span className="text-xs px-3 py-1 bg-red-500/20 border border-red-500/30 text-red-400 rounded-full">
                              65/67 FAIL
                            </span>
                          </div>
                          
                          <div className="flex items-center justify-between p-3 bg-muted/20 border border-muted/30 rounded-lg backdrop-blur-sm">
                            <div className="flex items-center gap-3">
                              <div className="w-2 h-2 rounded-full bg-green-400"></div>
                              <span className="text-sm font-medium text-foreground">API Endpoints</span>
                            </div>
                            <span className="text-xs px-3 py-1 bg-green-500/20 border border-green-500/30 text-green-400 rounded-full">
                              88/89 PASS
                            </span>
                          </div>
                          
                          <div className="flex items-center justify-between p-3 bg-muted/20 border border-muted/30 rounded-lg backdrop-blur-sm">
                            <div className="flex items-center gap-3">
                              <div className="w-2 h-2 rounded-full bg-green-400"></div>
                              <span className="text-sm font-medium text-foreground">UI Components</span>
                            </div>
                            <span className="text-xs px-3 py-1 bg-green-500/20 border border-green-500/30 text-green-400 rounded-full">
                              33/33 PASS
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Test Summary - Demo Data */}
                      <div>
                        <h3 className="font-semibold text-foreground mb-3">Test Summary</h3>
                        <div className="bg-muted/20 border border-muted/30 rounded-lg p-4">
                          <div className="grid grid-cols-2 gap-4 text-center">
                            <div>
                              <div className="text-2xl font-bold text-green-400">231</div>
                              <div className="text-xs text-muted-foreground">Tests Passed</div>
                            </div>
                            <div>
                              <div className="text-2xl font-bold text-red-400">3</div>
                              <div className="text-xs text-muted-foreground">Tests Failed</div>
                            </div>
                          </div>
                          <div className="mt-4">
                            <div className="flex justify-between text-sm mb-2">
                              <span className="text-muted-foreground">Coverage</span>
                              <span className="text-foreground font-medium">98.5%</span>
                            </div>
                            <div className="w-full bg-muted/30 rounded-full h-2">
                              <div className="bg-green-400 h-2 rounded-full" style={{width: '98.5%'}}></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      {/* Default content for other stages */}
                      <div>
                        <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                          <Zap className="w-5 h-5 text-orange-400" />
                          What this agent does
                        </h3>
                        <p className="text-muted-foreground leading-relaxed">{stage.details.action}</p>
                      </div>

                      {/* Example */}
                      <div>
                        <h3 className="font-semibold text-foreground mb-3">Latest Activity</h3>
                        <div className="bg-muted/20 border border-muted/30 rounded-lg p-4">
                          <p className="text-foreground italic">"{stage.details.example}"</p>
                        </div>
                      </div>

                      {/* Progress Logs */}
                      {stage.details.logs && stage.details.logs.length > 0 && (
                        <div>
                          <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-blue-400" />
                            Progress Logs
                          </h3>
                          <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4 font-mono text-sm max-h-32 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-transparent">
                            {stage.details.logs.map((log, index) => (
                              <motion.div
                                key={index}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.1 }}
                                className="text-green-400 mb-1 flex items-center gap-2"
                              >
                                <span className="text-muted-foreground">$</span>
                                {log}
                              </motion.div>
                            ))}
                            {stage.status === 'in_progress' && (
                              <motion.div
                                animate={{ opacity: [1, 0.5, 1] }}
                                transition={{ repeat: Infinity, duration: 1.5 }}
                                className="text-yellow-400 flex items-center gap-2"
                              >
                                <span className="text-muted-foreground">$</span>
                                <span className="inline-block w-2 h-4 bg-yellow-400 animate-pulse"></span>
                              </motion.div>
                            )}
                          </div>
                        </div>
                      )}
                    </>
                  )}

                {/* Agent Status */}
                <div className="flex items-center justify-between pt-4 border-t border-border/50">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      stage.status === 'completed' ? 'bg-green-400' :
                      stage.status === 'in_progress' ? 'bg-blue-400 animate-pulse' :
                      stage.status === 'failed' ? 'bg-red-400' : 'bg-muted'
                    }`} />
                    <span className="text-sm font-medium text-foreground">
                      Agent Status: {stage.status === 'in_progress' ? 'Working...' : 
                                   stage.status === 'completed' ? 'Completed' :
                                   stage.status === 'failed' ? 'Failed' : 'Waiting'}
                    </span>
                  </div>
                  
                  {stage.status === 'in_progress' && (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                      className="w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full"
                    />
                  )}
                </div>
              </div>
            </div>
          </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};