import React from 'react';
import { motion } from 'framer-motion';

interface FlowConnectionsProps {
  stages: Array<{ id: string; status: string }>;
  activeStageIndex: number;
  stagePositions: Array<{ x: number; y: number; width: number; height: number }>;
}

export const FlowConnections: React.FC<FlowConnectionsProps> = ({ 
  stages, 
  activeStageIndex, 
  stagePositions 
}) => {
  return (
    <svg 
      className="absolute inset-0 pointer-events-none z-10" 
      style={{ width: '100%', height: '100%' }}
    >
      {stagePositions.map((position, index) => {
        if (index >= stages.length - 1) return null;
        
        const nextPosition = stagePositions[index + 1];
        const isActive = index < activeStageIndex;
        const isCurrentFlow = index === activeStageIndex - 1;
        
        const startX = position.x + position.width;
        const startY = position.y + position.height / 2;
        const endX = nextPosition.x;
        const endY = nextPosition.y + nextPosition.height / 2;
        
        // Control points for smooth curve
        const controlX1 = startX + (endX - startX) * 0.3;
        const controlX2 = startX + (endX - startX) * 0.7;
        
        const pathData = `M ${startX} ${startY} C ${controlX1} ${startY} ${controlX2} ${endY} ${endX} ${endY}`;
        
        return (
          <g key={`connection-${index}`}>
            {/* Main connection line */}
            <motion.path
              d={pathData}
              fill="none"
              stroke={isActive ? "rgba(255, 255, 255, 0.6)" : "rgba(255, 255, 255, 0.2)"}
              strokeWidth={isActive ? "2" : "1"}
              initial={{ pathLength: 0 }}
              animate={{ 
                pathLength: isActive ? 1 : 0,
                stroke: isActive ? "rgba(255, 255, 255, 0.6)" : "rgba(255, 255, 255, 0.2)"
              }}
              transition={{ 
                duration: 1.5, 
                ease: "easeInOut",
                delay: index * 0.3 
              }}
              strokeDasharray={isCurrentFlow ? "5,5" : "none"}
            />
            
            {/* Animated flow particles - REMOVED */}
            {/* Flow particles animation has been removed */}
            
            {/* Arrow at the end */}
            {isActive && (
              <motion.polygon
                points={`${endX-8},${endY-4} ${endX},${endY} ${endX-8},${endY+4}`}
                fill="rgba(255, 255, 255, 0.6)"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.3 + 1 }}
              />
            )}
          </g>
        );
      })}
    </svg>
  );
};
