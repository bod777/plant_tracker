import React from 'react';

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

const NODE_RADIUS = 18;
const H_SPACING = 110;
const V_MARGIN = 20;

const TaxonomyChart: React.FC<TaxonomyChartProps> = ({ taxonomy }) => {
  const entries = LEVEL_ORDER
    .filter((level) => taxonomy[level])
    .map((level) => ({ level, value: taxonomy[level] }));

  if (entries.length === 0) return null;

  const width = H_SPACING * (entries.length - 1) + NODE_RADIUS * 2;
  const height = 80 + V_MARGIN * 2;

  return (
    <div className="overflow-x-auto">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-32"
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
          const x = NODE_RADIUS + idx * H_SPACING;
          const y = NODE_RADIUS + V_MARGIN;
          const nextX = NODE_RADIUS + (idx + 1) * H_SPACING;

          return (
            <g key={level}>
              {idx < entries.length - 1 && (
                <line
                  x1={x}
                  y1={y}
                  x2={nextX}
                  y2={y}
                  stroke="#22c55e"
                  strokeWidth={2}
                  markerEnd="url(#arrow)"
                />
              )}
              <circle cx={x} cy={y} r={NODE_RADIUS} fill="#4ade80" />
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                className="fill-white text-xs capitalize"
              >
                {level[0]}
              </text>
              <text
                x={x}
                y={y + NODE_RADIUS + 12}
                textAnchor="middle"
                className="text-xs"
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
