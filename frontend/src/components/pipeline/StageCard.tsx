import React from 'react';
import { motion } from 'framer-motion';
import { Stage } from './PipelineFlow';

interface StageCardProps {
  stage: Stage;
  isActive: boolean;
  onClick: () => void;
  isCompact?: boolean;
}

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'pending':
      return (
        <span className="status-badge status-pending">
          <div className="w-2 h-2 rounded-full bg-muted-foreground" />
          Pending
        </span>
      );
    case 'progress':
      return (
        <span className="status-badge status-progress">
          <motion.div
            className="w-2 h-2 rounded-full bg-blue-400"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
          />
          In Progress
        </span>
      );
    case 'completed':
      return (
        <span className="status-badge status-completed">
          <div className="w-2 h-2 rounded-full bg-green-400" />
          Completed
        </span>
      );
    case 'failed':
      return (
        <span className="status-badge status-failed">
          <div className="w-2 h-2 rounded-full bg-red-400" />
          Failed
        </span>
      );
    default:
      return null;
  }
};

const getStageClassName = (id: string) => {
  const baseClass = 'stage-card';
  switch (id) {
    case 'pr': return `${baseClass} stage-pr`;
    case 'build': return `${baseClass} stage-build`;
    case 'analyze': return `${baseClass} stage-analyze`;
    case 'fix': return `${baseClass} stage-fix`;
    case 'test': return `${baseClass} stage-test`;
    case 'results': return `${baseClass} stage-results`;
    default: return baseClass;
  }
};

const getAgentClassName = (id: string) => {
  switch (id) {
    case 'pr': return 'agent-avatar agent-pr';
    case 'build': return 'agent-avatar agent-build';
    case 'analyze': return 'agent-avatar agent-analyze';
    case 'fix': return 'agent-avatar agent-fix';
    case 'test': return 'agent-avatar agent-test';
    case 'results': return 'agent-avatar agent-results';
    default: return 'agent-avatar';
  }
};

export const StageCard: React.FC<StageCardProps> = ({ stage, isActive, onClick, isCompact = false }) => {
  const cardSize = isCompact ? 'w-32 h-44' : 'w-40 h-56';
  
  return (
    <motion.div
      className={`${getStageClassName(stage.id)} ${isActive ? 'active' : ''} ${cardSize} min-w-[8rem] group relative cursor-pointer`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      layout
    >
      {/* Stage Icon */}
      <div className="flex items-center justify-center mb-3">
        <motion.div
          className={isCompact ? "text-2xl mb-2" : "text-3xl mb-2"}
          animate={isActive ? { rotate: [0, 5, -5, 0] } : {}}
          transition={{ repeat: isActive ? Infinity : 0, duration: 2 }}
        >
          {stage.icon}
        </motion.div>
      </div>

      {/* Agent Avatar */}
      <div className="absolute top-3 right-3">
        <div className={`${getAgentClassName(stage.id)} text-xs w-6 h-6`} title={`${stage.agent} Agent`}>
          {stage.agent}
        </div>
      </div>

      {/* Stage Info */}
      <div className="text-center px-2">
        <h3 className={`font-semibold text-foreground mb-2 ${isCompact ? 'text-xs' : 'text-sm'}`}>{stage.name}</h3>
        <p className={`text-muted-foreground mb-4 leading-relaxed ${isCompact ? 'text-[10px]' : 'text-xs'}`}>{stage.description}</p>
        
        {/* Status Badge */}
        <div className="flex justify-center">
          {getStatusBadge(stage.status)}
        </div>
      </div>

      {/* Click hint */}
      <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 text-xs text-muted-foreground/60 opacity-0 group-hover:opacity-100 transition-opacity">
        Click for details
      </div>
    </motion.div>
  );
};