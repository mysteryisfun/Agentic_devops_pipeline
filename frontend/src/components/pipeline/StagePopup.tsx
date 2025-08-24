import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Zap, Clock, AlertTriangle, CheckCircle, XCircle, Bot, Shield, Package, Search, Wrench, TestTube, BarChart3 } from 'lucide-react';
import { Stage } from './PipelineFlow';

interface StagePopupProps {
  stage: Stage | null;
  isVisible: boolean;
  position: { x: number; y: number };
  isLeftSide?: boolean;
  isClickedMode?: boolean; // Keep for compatibility but won't use clicked mode
  onClose?: () => void;
}

export const StagePopup: React.FC<StagePopupProps> = ({ 
  stage, 
  isVisible, 
  position
}) => {
  if (!stage) return null;

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 20 }}
          transition={{ type: "spring", damping: 20, stiffness: 300 }}
          className="absolute z-30 w-[520px] h-[380px]"
          style={{
            left: position.x,
            top: position.y,
          }}
        >
          <div className="bg-card/90 backdrop-blur-sm rounded-xl shadow-xl border border-border/30 overflow-hidden h-full">
            {/* Auto-focus view with detailed content */}
            <div className="p-6 flex flex-col h-full overflow-y-auto">
              {/* Stage Header */}
              <div className="flex items-center gap-4 mb-6">
                <div className="text-3xl">{stage.icon}</div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-foreground mb-1">
                    {stage.name}
                  </h3>
                  <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4" />
                    <span className="text-primary font-medium text-sm">
                      {stage.agent} Agent
                    </span>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 space-y-4 overflow-y-auto">
                {/* Build Stage Content */}
                {stage.id === 'build' && stage.results ? (
                  <>
                    {/* Build Status */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <Zap className="w-4 h-4 text-blue-400" />
                        Build Status
                      </h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          {stage.results.files_analyzed && (
                            <div>
                              <span className="text-muted-foreground">Files Processed:</span>
                              <span className="text-foreground font-medium ml-2">{stage.results.files_analyzed} files</span>
                            </div>
                          )}
                          {stage.results.dependencies_found && (
                            <div>
                              <span className="text-muted-foreground">Dependencies:</span>
                              <span className="text-foreground font-medium ml-2">{stage.results.dependencies_found} packages</span>
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

                    {/* Build Logs */}
                    {stage.results.build_logs && stage.results.build_logs.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-green-400" />
                          Recent Activity
                        </h3>
                        <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 font-mono text-xs max-h-24 overflow-y-auto">
                          {stage.results.build_logs.slice(-4).map((log, index) => (
                            <div key={index} className="text-green-400 mb-1">
                              {log}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Build Errors */}
                    {stage.results.errors && stage.results.errors.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <XCircle className="w-4 h-4 text-red-400" />
                          Build Errors
                        </h3>
                        <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-3 font-mono text-xs max-h-24 overflow-y-auto">
                          {stage.results.errors.map((error, index) => (
                            <div key={index} className="text-red-400 mb-1">
                              {error}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : stage.id === 'analyze' && stage.results ? (
                  <>
                    {/* Analysis Overview */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <Zap className="w-4 h-4 text-purple-400" />
                        Analysis Overview
                      </h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="grid grid-cols-2 gap-3 text-xs">
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

                    {/* Vulnerabilities */}
                    {stage.results.vulnerabilities && stage.results.vulnerabilities.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <AlertTriangle className="w-4 h-4 text-red-400" />
                          Vulnerabilities ({stage.results.vulnerabilities.length})
                        </h3>
                        <div className="space-y-2 max-h-32 overflow-y-auto">
                          {stage.results.vulnerabilities.slice(0, 3).map((vuln, index) => (
                            <div key={index} className="bg-red-900/20 border border-red-700/50 rounded-lg p-2">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-xs font-medium text-red-400">{vuln.type}</span>
                                <span className={`text-xs px-2 py-0.5 rounded-full ${
                                  vuln.severity === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                                  vuln.severity === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                                  'bg-blue-500/20 text-blue-400'
                                }`}>
                                  {vuln.severity}
                                </span>
                              </div>
                              <p className="text-xs text-muted-foreground mb-1">{vuln.description}</p>
                              <div className="text-xs text-muted-foreground">
                                {vuln.file}:{vuln.line} • Confidence: {Math.round(vuln.confidence * 100)}%
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* AI Metadata */}
                    {stage.results.metadata && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <Bot className="w-4 h-4 text-blue-400" />
                          AI Analysis Info
                        </h3>
                        <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                          <div className="grid grid-cols-1 gap-2 text-xs">
                            {stage.results.metadata.mcp_questions_asked && (
                              <div>
                                <span className="text-muted-foreground">MCP Questions:</span>
                                <span className="text-foreground font-medium ml-2">{stage.results.metadata.mcp_questions_asked}</span>
                              </div>
                            )}
                            {stage.results.metadata.ai_model && (
                              <div>
                                <span className="text-muted-foreground">AI Model:</span>
                                <span className="text-foreground font-medium ml-2">{stage.results.metadata.ai_model}</span>
                              </div>
                            )}
                            {stage.results.metadata.context_gathered && (
                              <div>
                                <span className="text-muted-foreground">Context Size:</span>
                                <span className="text-foreground font-medium ml-2">{stage.results.metadata.context_gathered}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                ) : stage.id === 'test' && stage.results ? (
                  <>
                    {/* Test Results - Real Data */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <Zap className="w-4 h-4 text-orange-400" />
                        Test Results
                      </h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          {stage.results.total_tests && (
                            <div>
                              <span className="text-muted-foreground">Total Tests:</span>
                              <span className="text-foreground font-medium ml-2">{stage.results.total_tests}</span>
                            </div>
                          )}
                          {stage.results.passed_tests !== undefined && (
                            <div>
                              <span className="text-muted-foreground">Passed:</span>
                              <span className="text-green-400 font-medium ml-2">{stage.results.passed_tests}</span>
                            </div>
                          )}
                          {stage.results.failed_tests !== undefined && (
                            <div>
                              <span className="text-muted-foreground">Failed:</span>
                              <span className="text-red-400 font-medium ml-2">{stage.results.failed_tests}</span>
                            </div>
                          )}
                          {stage.results.coverage && (
                            <div>
                              <span className="text-muted-foreground">Coverage:</span>
                              <span className="text-foreground font-medium ml-2">{stage.results.coverage}%</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Test Logs - Real Data */}
                    {stage.results.test_logs && stage.results.test_logs.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-green-400" />
                          Test Logs
                        </h3>
                        <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 font-mono text-xs max-h-24 overflow-y-auto">
                          {stage.results.test_logs.map((log, index) => (
                            <div key={index} className="text-green-400 mb-1">
                              <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span> {log}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Test Failures - Real Data */}
                    {stage.results.test_failures && stage.results.test_failures.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <XCircle className="w-4 h-4 text-red-400" />
                          Test Failures ({stage.results.test_failures.length})
                        </h3>
                        <div className="space-y-2 max-h-32 overflow-y-auto">
                          {stage.results.test_failures.slice(0, 3).map((failure, index) => (
                            <div key={index} className="bg-red-900/20 border border-red-700/50 rounded-lg p-2">
                              <div className="text-xs font-medium text-red-400 mb-1">{failure.test_name}</div>
                              <p className="text-xs text-muted-foreground mb-1">{failure.error_message}</p>
                              <div className="text-xs text-muted-foreground">
                                {failure.file}:{failure.line}
                              </div>
                            </div>
                          ))}
                          {stage.results.test_failures.length > 3 && (
                            <div className="text-xs text-center text-muted-foreground py-1">
                              +{stage.results.test_failures.length - 3} more failures
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </>
                ) : stage.id === 'fix' && stage.results ? (
                  <>
                    {/* Fix Results - Real Data */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <Zap className="w-4 h-4 text-purple-400" />
                        Fix Results
                      </h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          {stage.results.fixes_applied && (
                            <div>
                              <span className="text-muted-foreground">Fixes Applied:</span>
                              <span className="text-green-400 font-medium ml-2">{stage.results.fixes_applied}</span>
                            </div>
                          )}
                          {stage.results.remaining_issues !== undefined && (
                            <div>
                              <span className="text-muted-foreground">Remaining Issues:</span>
                              <span className="text-orange-400 font-medium ml-2">{stage.results.remaining_issues}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Issues Resolved - Real Data */}
                    {stage.results.issues_resolved && stage.results.issues_resolved.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <CheckCircle className="w-4 h-4 text-green-400" />
                          Issues Resolved ({stage.results.issues_resolved.length})
                        </h3>
                        <div className="space-y-2 max-h-32 overflow-y-auto">
                          {stage.results.issues_resolved.slice(0, 3).map((issue, index) => (
                            <div key={index} className="bg-green-900/20 border border-green-700/50 rounded-lg p-2">
                              <div className="text-xs font-medium text-green-400 mb-1">{issue.type}</div>
                              <p className="text-xs text-muted-foreground mb-1">{issue.description}</p>
                              <div className="text-xs text-blue-400 mb-1">Fix: {issue.fix_applied}</div>
                              <div className="text-xs text-muted-foreground">
                                {issue.file}:{issue.line} • Confidence: {Math.round(issue.confidence * 100)}%
                              </div>
                            </div>
                          ))}
                          {stage.results.issues_resolved.length > 3 && (
                            <div className="text-xs text-center text-muted-foreground py-1">
                              +{stage.results.issues_resolved.length - 3} more issues resolved
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Fix Logs - Real Data */}
                    {stage.results.fix_logs && stage.results.fix_logs.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-blue-400" />
                          Fix Logs
                        </h3>
                        <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 font-mono text-xs max-h-24 overflow-y-auto">
                          {stage.results.fix_logs.map((log, index) => (
                            <div key={index} className="text-green-400 mb-1">
                              <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span> {log}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : stage.id === 'results' && stage.results ? (
                  <>
                    {/* Pipeline Results - Real Data */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        Pipeline Summary
                      </h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="space-y-2 text-xs">
                          {stage.results.overall_status && (
                            <div className="flex items-center justify-between">
                              <span className="text-muted-foreground">Overall Status:</span>
                              <span className={`font-medium px-2 py-0.5 rounded-full ${
                                stage.results.overall_status === 'success' ? 'bg-green-500/20 text-green-400' :
                                stage.results.overall_status === 'partial' ? 'bg-yellow-500/20 text-yellow-400' :
                                'bg-red-500/20 text-red-400'
                              }`}>
                                {stage.results.overall_status.toUpperCase()}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Summary Stats - Real Data */}
                    {stage.results.summary && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <Bot className="w-4 h-4 text-blue-400" />
                          Summary Stats
                        </h3>
                        <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                          <div className="grid grid-cols-2 gap-3 text-xs">
                            <div>
                              <span className="text-muted-foreground">Issues Found:</span>
                              <span className="text-foreground font-medium ml-2">{stage.results.summary.total_issues_found}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Issues Fixed:</span>
                              <span className="text-green-400 font-medium ml-2">{stage.results.summary.issues_fixed}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Tests Passed:</span>
                              <span className="text-green-400 font-medium ml-2">{stage.results.summary.tests_passed}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Coverage Improved:</span>
                              <span className="text-blue-400 font-medium ml-2">+{stage.results.summary.coverage_improvement}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                ) : stage.id === 'build' ? (
                  <>
                    {/* Build Stage - No Results Yet */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <Package className="w-4 h-4 text-green-400" />
                        Build Process
                      </h3>
                      <p className="text-muted-foreground leading-relaxed text-xs">{stage.details.action}</p>
                    </div>

                    <div>
                      <h3 className="font-semibold text-foreground mb-2 text-sm">Build Status</h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            stage.status === 'success' ? 'bg-green-400' :
                            stage.status === 'in_progress' ? 'bg-blue-400 animate-pulse' :
                            stage.status === 'failed' ? 'bg-red-400' :
                            'bg-slate-400'
                          }`}></div>
                          <span className="text-xs text-foreground capitalize">
                            {stage.status === 'in_progress' ? 'Building...' : 
                             stage.status === 'pending' ? 'Ready to Build' :
                             stage.status === 'success' ? 'Build Complete' : stage.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    {stage.details.logs && stage.details.logs.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-green-400" />
                          Build Activity
                        </h3>
                        <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 font-mono text-xs max-h-24 overflow-y-auto">
                          {stage.details.logs.map((log, index) => (
                            <div key={index} className="text-green-400 mb-1">
                              <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span> {log}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : stage.id === 'analyze' ? (
                  <>
                    {/* Analyze Stage - No Results Yet */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <Search className="w-4 h-4 text-purple-400" />
                        AI Code Analysis
                      </h3>
                      <p className="text-muted-foreground leading-relaxed text-xs">{stage.details.action}</p>
                    </div>

                    <div>
                      <h3 className="font-semibold text-foreground mb-2 text-sm">Analysis Status</h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            stage.status === 'success' ? 'bg-green-400' :
                            stage.status === 'in_progress' ? 'bg-purple-400 animate-pulse' :
                            stage.status === 'failed' ? 'bg-red-400' :
                            'bg-slate-400'
                          }`}></div>
                          <span className="text-xs text-foreground capitalize">
                            {stage.status === 'in_progress' ? 'Analyzing Code...' : 
                             stage.status === 'pending' ? 'Ready to Analyze' :
                             stage.status === 'success' ? 'Analysis Complete' : stage.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    {stage.details.logs && stage.details.logs.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-purple-400" />
                          Analysis Activity
                        </h3>
                        <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 font-mono text-xs max-h-24 overflow-y-auto">
                          {stage.details.logs.map((log, index) => (
                            <div key={index} className="text-purple-400 mb-1">
                              <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span> {log}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : stage.id === 'fix' ? (
                  <>
                    {/* Fix Stage - No Results Yet */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <Wrench className="w-4 h-4 text-orange-400" />
                        Auto Fix System
                      </h3>
                      <p className="text-muted-foreground leading-relaxed text-xs">{stage.details.action}</p>
                    </div>

                    <div>
                      <h3 className="font-semibold text-foreground mb-2 text-sm">Fix Status</h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            stage.status === 'success' ? 'bg-green-400' :
                            stage.status === 'in_progress' ? 'bg-orange-400 animate-pulse' :
                            stage.status === 'failed' ? 'bg-red-400' :
                            'bg-slate-400'
                          }`}></div>
                          <span className="text-xs text-foreground capitalize">
                            {stage.status === 'in_progress' ? 'Applying Fixes...' : 
                             stage.status === 'pending' ? 'Ready to Fix' :
                             stage.status === 'success' ? 'Fixes Applied' : stage.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    {stage.details.logs && stage.details.logs.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-orange-400" />
                          Fix Activity
                        </h3>
                        <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 font-mono text-xs max-h-24 overflow-y-auto">
                          {stage.details.logs.map((log, index) => (
                            <div key={index} className="text-orange-400 mb-1">
                              <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span> {log}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : stage.id === 'test' ? (
                  <>
                    {/* Test Stage - No Results Yet */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <TestTube className="w-4 h-4 text-blue-400" />
                        Testing Suite
                      </h3>
                      <p className="text-muted-foreground leading-relaxed text-xs">{stage.details.action}</p>
                    </div>

                    <div>
                      <h3 className="font-semibold text-foreground mb-2 text-sm">Test Status</h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            stage.status === 'success' ? 'bg-green-400' :
                            stage.status === 'in_progress' ? 'bg-blue-400 animate-pulse' :
                            stage.status === 'failed' ? 'bg-red-400' :
                            'bg-slate-400'
                          }`}></div>
                          <span className="text-xs text-foreground capitalize">
                            {stage.status === 'in_progress' ? 'Running Tests...' : 
                             stage.status === 'pending' ? 'Ready to Test' :
                             stage.status === 'success' ? 'Tests Passed' : stage.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    {stage.details.logs && stage.details.logs.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-blue-400" />
                          Test Activity
                        </h3>
                        <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 font-mono text-xs max-h-24 overflow-y-auto">
                          {stage.details.logs.map((log, index) => (
                            <div key={index} className="text-blue-400 mb-1">
                              <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span> {log}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : stage.id === 'results' ? (
                  <>
                    {/* Results Stage - No Results Yet */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <BarChart3 className="w-4 h-4 text-green-400" />
                        Pipeline Summary
                      </h3>
                      <p className="text-muted-foreground leading-relaxed text-xs">{stage.details.action}</p>
                    </div>

                    <div>
                      <h3 className="font-semibold text-foreground mb-2 text-sm">Summary Status</h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            stage.status === 'success' ? 'bg-green-400' :
                            stage.status === 'in_progress' ? 'bg-green-400 animate-pulse' :
                            stage.status === 'failed' ? 'bg-red-400' :
                            'bg-slate-400'
                          }`}></div>
                          <span className="text-xs text-foreground capitalize">
                            {stage.status === 'in_progress' ? 'Generating Summary...' : 
                             stage.status === 'pending' ? 'Waiting for Pipeline' :
                             stage.status === 'success' ? 'Summary Ready' : stage.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    {stage.details.logs && stage.details.logs.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-green-400" />
                          Summary Activity
                        </h3>
                        <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 font-mono text-xs max-h-24 overflow-y-auto">
                          {stage.details.logs.map((log, index) => (
                            <div key={index} className="text-green-400 mb-1">
                              <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span> {log}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <>
                    {/* Generic fallback for any stage without results */}
                    <div>
                      <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2 text-sm">
                        <Zap className="w-4 h-4 text-orange-400" />
                        Stage Information
                      </h3>
                      <p className="text-muted-foreground leading-relaxed text-xs">{stage.details?.action || 'This stage is preparing to run.'}</p>
                    </div>

                    <div>
                      <h3 className="font-semibold text-foreground mb-2 text-sm">Current Status</h3>
                      <div className="bg-muted/20 border border-muted/30 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            stage.status === 'success' ? 'bg-green-400' :
                            stage.status === 'in_progress' ? 'bg-blue-400 animate-pulse' :
                            stage.status === 'failed' ? 'bg-red-400' :
                            'bg-slate-400'
                          }`}></div>
                          <span className="text-xs text-foreground capitalize">
                            {stage.status === 'in_progress' ? 'In Progress' : stage.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default StagePopup;
