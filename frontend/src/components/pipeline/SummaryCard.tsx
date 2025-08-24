import React from 'react';
import { motion } from 'framer-motion';
import { GitPullRequest, Bug, TestTube, CheckCircle, XCircle } from 'lucide-react';

interface SummaryData {
  prStatus: string;
  issuesFixed: number;
  testCoverage: number;
  mergeReadiness: string;
}

interface SummaryCardProps {
  data: SummaryData;
}

export const SummaryCard: React.FC<SummaryCardProps> = ({ data }) => {
  const isReady = data.mergeReadiness === 'Ready';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="bg-card/90 backdrop-blur-xl rounded-lg p-3 shadow-lg border border-border/50"
    >
      <div className="flex items-center justify-between">
        {/* Left side - Title and Ready Status */}
        <div className="flex items-center gap-4">
          <h3 className="text-base font-semibold text-foreground">Pipeline Summary</h3>
          <motion.div
            className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${
              isReady 
                ? 'bg-green-500/10 border-green-500/30 text-green-400' 
                : 'bg-orange-500/10 border-orange-500/30 text-orange-400'
            }`}
          >
            {isReady ? (
              <CheckCircle className="w-3 h-3" />
            ) : (
              <XCircle className="w-3 h-3" />
            )}
            {data.mergeReadiness}
          </motion.div>
        </div>

        {/* Center - Compact Stats */}
        <div className="flex items-center gap-6">
          {/* PR Status */}
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-blue-500/20 border border-blue-500/30 rounded backdrop-blur-sm">
              <GitPullRequest className="w-3 h-3 text-blue-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">PR Status</p>
              <p className="text-sm font-semibold text-foreground">{data.prStatus}</p>
            </div>
          </div>

          {/* Issues Fixed */}
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-orange-500/20 border border-orange-500/30 rounded backdrop-blur-sm">
              <Bug className="w-3 h-3 text-orange-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Issues Fixed</p>
              <motion.p 
                className="text-sm font-semibold text-foreground"
                key={data.issuesFixed}
                initial={{ scale: 1.2, color: '#fb923c' }}
                animate={{ scale: 1, color: 'inherit' }}
                transition={{ duration: 0.3 }}
              >
                {data.issuesFixed}
              </motion.p>
            </div>
          </div>
        </div>

        {/* Right side - Progress */}
        <div className="flex items-center gap-3">
          <div>
            <p className="text-xs text-muted-foreground text-right">Overall Progress</p>
            <p className="text-sm font-medium text-foreground text-right">60%</p>
          </div>
          <div className="w-32 bg-gray-700 rounded-full h-1">
            <motion.div
              className="bg-white h-1 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: '60%' }}
              transition={{ duration: 1.5, delay: 0.8 }}
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
};