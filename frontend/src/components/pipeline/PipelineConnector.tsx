import React from 'react';
import { motion } from 'framer-motion';
import { ChevronRight } from 'lucide-react';

interface PipelineConnectorProps {
  isActive: boolean;
}

export const PipelineConnector: React.FC<PipelineConnectorProps> = ({ isActive }) => {
  return (
    <div className={`pipeline-connector w-12 h-10 ${isActive ? 'active' : ''}`}>
      <motion.div
        className={`flex items-center justify-center w-6 h-6 rounded-full ${
          isActive 
            ? 'bg-blue-500 text-white shadow-lg' 
            : 'bg-muted/30 text-muted-foreground'
        }`}
        animate={isActive ? { 
          scale: [1, 1.2, 1],
          boxShadow: ['0 0 0 0 rgba(59, 130, 246, 0.7)', '0 0 0 8px rgba(59, 130, 246, 0)', '0 0 0 0 rgba(59, 130, 246, 0)']
        } : {}}
        transition={{ 
          duration: 2, 
          repeat: isActive ? Infinity : 0,
          ease: "easeInOut"
        }}
      >
        <ChevronRight className="w-3 h-3" />
      </motion.div>
    </div>
  );
};