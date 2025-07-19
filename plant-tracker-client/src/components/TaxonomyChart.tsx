import React from 'react';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils';

interface TaxonomyChartProps {
  taxonomy: Record<string, string>;
}

const LEVEL_ORDER = [
  'kingdom',
  'phylum',
  'class',
  'order',
  'family',
  'genus',
  'species',
];

const DEFAULT_NODE_RADIUS = 18;
const DEFAULT_SPACING = 110;
const DEFAULT_MARGIN = 20;
const TEXT_OFFSET = 12;

const MOBILE_NODE_RADIUS = 14;
const MOBILE_SPACING = 80;
const MOBILE_MARGIN = 10;

const TaxonomyChart: React.FC<TaxonomyChartProps> = ({ taxonomy }) => {
  const isMobile = useIsMobile();

  const NODE_RADIUS = isMobile ? MOBILE_NODE_RADIUS : DEFAULT_NODE_RADIUS;
  const SPACING = isMobile ? MOBILE_SPACING : DEFAULT_SPACING;
  const MARGIN = isMobile ? MOBILE_MARGIN : DEFAULT_MARGIN;

  const BASE_HEIGHT = 100;

  const entries = LEVEL_ORDER
    .filter((level) => taxonomy[level])
    .map((level) => ({ level, value: taxonomy[level] }));

  if (entries.length === 0) return null;

  const width = isMobile
    ? NODE_RADIUS * 2 + MARGIN * 2
    : SPACING * (entries.length - 1) + NODE_RADIUS * 2;
  const height = isMobile
    ? SPACING * (entries.length - 1) + NODE_RADIUS * 2 + MARGIN * 2
    : BASE_HEIGHT + MARGIN * 2;

  return (
    <div className={cn(isMobile ? 'overflow-y-auto' : 'overflow-x-auto')}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className={cn('w-full', isMobile ? '' : 'h-32')}
        style={isMobile ? { height } : undefined}
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 6 6"
            refX="5"
            refY="3"
            markerWidth="6"
            markerHeight="6"
            orient="auto"
          >
            <path d="M0 0 L6 3 L0 6 Z" fill="#22c55e" />
          </marker>
        </defs>
        {entries.map(({ level, value }, idx) => {
          const x = isMobile
            ? NODE_RADIUS + MARGIN
            : NODE_RADIUS + idx * SPACING;
          const y = isMobile
            ? NODE_RADIUS + MARGIN + TEXT_OFFSET + idx * SPACING
            : NODE_RADIUS + MARGIN + TEXT_OFFSET;
          const nextX = isMobile ? x : NODE_RADIUS + (idx + 1) * SPACING;
          const nextY = NODE_RADIUS + MARGIN + TEXT_OFFSET + (idx + 1) * SPACING;

          return (
            <g key={level}>
              {idx < entries.length - 1 && (
                <line
                  x1={x}
                  y1={y}
                  x2={isMobile ? x : nextX}
                  y2={isMobile ? nextY : y}
                  stroke="#22c55e"
                  strokeWidth={2}
                  markerEnd="url(#arrow)"
                />
              )}
              <text
                x={x}
                y={y - NODE_RADIUS - TEXT_OFFSET / 2}
                textAnchor="middle"
                className={cn('capitalize text-gray-700', isMobile ? 'text-[10px]' : 'text-xs')}
              >
                {level}
              </text>
              <circle cx={x} cy={y} r={NODE_RADIUS} fill="#4ade80" />
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                className={cn('fill-white', isMobile ? 'text-[10px]' : 'text-xs')}
              >
                {level[0].toUpperCase()}
              </text>
              <text
                x={x}
                y={y + NODE_RADIUS + TEXT_OFFSET}
                textAnchor="middle"
                className={cn(isMobile ? 'text-[10px]' : 'text-xs')}
              >
                {value}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export default TaxonomyChart;
