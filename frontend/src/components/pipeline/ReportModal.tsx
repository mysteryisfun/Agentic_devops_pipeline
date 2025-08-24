import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertTriangle, Bug, TestTube, GitPullRequest, Download } from 'lucide-react';

interface ReportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ReportModal: React.FC<ReportModalProps> = ({ isOpen, onClose }) => {
  const reportData = {
    summary: {
      totalIssues: 10,
      fixedIssues: 8,
      testsPassed: 234,
      testsFailed: 3,
      coverage: 98.5,
      buildTime: '2m 34s',
      pipelineStatus: 'Success'
    },
    issues: [
      { type: 'Security', description: 'SQL injection vulnerability fixed', status: 'fixed' },
      { type: 'Performance', description: 'Database query optimization', status: 'fixed' },
      { type: 'Bug', description: 'Null pointer exception handling', status: 'fixed' },
      { type: 'Code Quality', description: 'Unused import removal', status: 'fixed' },
      { type: 'Security', description: 'XSS vulnerability patched', status: 'fixed' },
      { type: 'Performance', description: 'Memory leak in event handlers', status: 'fixed' },
      { type: 'Bug', description: 'Race condition in async operations', status: 'fixed' },
      { type: 'Code Quality', description: 'Dead code elimination', status: 'fixed' },
      { type: 'Critical', description: 'Authentication bypass attempt', status: 'pending' },
      { type: 'Warning', description: 'Deprecated API usage', status: 'pending' }
    ],
    testResults: [
      { suite: 'Authentication', tests: 45, passed: 45, failed: 0 },
      { suite: 'Database', tests: 67, passed: 65, failed: 2 },
      { suite: 'API Endpoints', tests: 89, passed: 88, failed: 1 },
      { suite: 'UI Components', tests: 33, passed: 33, failed: 0 }
    ]
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
              className="w-full max-w-5xl max-h-[90vh]"
            >
            <div className="bg-card/95 backdrop-blur-xl rounded-2xl shadow-2xl overflow-hidden border border-border/50">
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-cyan-500/10 backdrop-blur-sm p-6 border-b border-border/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center">
                      <GitPullRequest className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-foreground">Pipeline Report</h2>
                      <p className="text-muted-foreground">PR #247 - Add user authentication feature</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                      <Download className="w-4 h-4" />
                      Download PDF
                    </button>
                    <button
                      onClick={onClose}
                      className="p-2 hover:bg-muted/50 rounded-full transition-colors"
                    >
                      <X className="w-5 h-5 text-muted-foreground hover:text-foreground" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Content - Improved scrolling */}
              <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)] scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent">
                {/* Summary Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                  <div className="bg-muted/20 border border-muted/30 rounded-lg p-4 text-center backdrop-blur-sm">
                    <div className="text-2xl font-bold text-green-400">{reportData.summary.fixedIssues}</div>
                    <div className="text-sm text-muted-foreground">Issues Fixed</div>
                  </div>
                  <div className="bg-muted/20 border border-muted/30 rounded-lg p-4 text-center backdrop-blur-sm">
                    <div className="text-2xl font-bold text-primary">{reportData.summary.testsPassed}</div>
                    <div className="text-sm text-muted-foreground">Tests Passed</div>
                  </div>
                  <div className="bg-muted/20 border border-muted/30 rounded-lg p-4 text-center backdrop-blur-sm">
                    <div className="text-2xl font-bold text-cyan-400">{reportData.summary.coverage}%</div>
                    <div className="text-sm text-muted-foreground">Coverage</div>
                  </div>
                  <div className="bg-muted/20 border border-muted/30 rounded-lg p-4 text-center backdrop-blur-sm">
                    <div className="text-2xl font-bold text-foreground">{reportData.summary.buildTime}</div>
                    <div className="text-sm text-muted-foreground">Build Time</div>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Issues Fixed */}
                  <div>
                    <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
                      <Bug className="w-5 h-5 text-orange-400" />
                      Issues Detected & Fixed
                    </h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent">
                      {reportData.issues.map((issue, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="flex items-center justify-between p-3 bg-muted/20 border border-muted/30 rounded-lg backdrop-blur-sm"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`text-xs px-2 py-1 rounded ${
                                issue.type === 'Security' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                                issue.type === 'Performance' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                                issue.type === 'Bug' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                                issue.type === 'Critical' ? 'bg-red-600/20 text-red-300 border border-red-600/30' :
                                'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                              }`}>
                                {issue.type}
                              </span>
                            </div>
                            <p className="text-sm text-foreground">{issue.description}</p>
                          </div>
                          <div className="ml-3">
                            {issue.status === 'fixed' ? (
                              <CheckCircle className="w-5 h-5 text-green-400" />
                            ) : (
                              <AlertTriangle className="w-5 h-5 text-yellow-400" />
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  {/* Test Results */}
                  <div>
                    <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
                      <TestTube className="w-5 h-5 text-green-400" />
                      Test Results
                    </h3>
                    <div className="space-y-3">
                      {reportData.testResults.map((suite, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: 10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="p-3 bg-muted/20 border border-muted/30 rounded-lg backdrop-blur-sm"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-foreground">{suite.suite}</span>
                            <span className="text-sm text-muted-foreground">
                              {suite.tests} tests
                            </span>
                          </div>
                          <div className="flex items-center gap-4 text-sm">
                            <span className="text-green-400">✓ {suite.passed} passed</span>
                            {suite.failed > 0 && (
                              <span className="text-red-400">✗ {suite.failed} failed</span>
                            )}
                          </div>
                          <div className="mt-2 w-full bg-muted/30 rounded-full h-2">
                            <div 
                              className="bg-green-400 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${(suite.passed / suite.tests) * 100}%` }}
                            />
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Final Status */}
                <div className="mt-8 p-4 bg-green-500/10 border border-green-400/30 rounded-lg backdrop-blur-sm">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-6 h-6 text-green-400" />
                    <div>
                      <h4 className="font-semibold text-green-400">Pipeline Completed Successfully</h4>
                      <p className="text-sm text-muted-foreground">
                        All critical issues have been resolved. This PR is ready for review and merge.
                      </p>
                    </div>
                  </div>
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