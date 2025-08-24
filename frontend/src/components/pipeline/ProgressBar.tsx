import React from 'react';
import { motion } from 'framer-motion';

interface ProgressBarProps {
  progress: number;
  currentStage: number;
}

const stageNames = ['PR Created', 'Building', 'Analyzing', 'Fixing', 'Testing', 'Complete'];

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress, currentStage }) => {
  return (
    <div className="mb-12">
      {/* Progress Steps */}
      <div className="flex items-center justify-between mb-4 px-4">
        {stageNames.map((name, index) => (
          <div key={name} className="flex flex-col items-center flex-1 min-w-0">
            <motion.div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all duration-300 ${
                index <= currentStage
                  ? 'bg-blue-500 text-white border-blue-400 shadow-lg shadow-blue-500/25'
                  : 'bg-muted/30 text-muted-foreground border-muted'
              }`}
              initial={{ scale: 0.8 }}
              animate={{ 
                scale: index === currentStage ? [1, 1.1, 1] : 1,
                rotate: index === currentStage ? [0, 5, -5, 0] : 0
              }}
              transition={{ 
                scale: { repeat: index === currentStage ? Infinity : 0, duration: 2 },
                rotate: { repeat: index === currentStage ? Infinity : 0, duration: 2 }
              }}
            >
              {index + 1}
            </motion.div>
            <span className={`text-xs mt-2 text-center ${
              index <= currentStage ? 'text-blue-400 font-medium' : 'text-muted-foreground'
            }`}>
              {name}
            </span>
          </div>
        ))}
      </div>

      {/* Progress Bar */}
      <div className="progress-bar bg-muted/30 rounded-full h-2 overflow-hidden backdrop-blur-sm border border-muted/20">
        <motion.div
          className="progress-fill h-full bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-400 rounded-full shadow-lg"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </div>

      {/* Progress Text */}
      <div className="flex justify-between items-center mt-2">
        <span className="text-sm text-muted-foreground">
          Stage {currentStage + 1} of {stageNames.length}
        </span>
        <span className="text-sm font-medium text-foreground">
          {Math.round(progress)}% Complete
        </span>
      </div>
    </div>
  );
};