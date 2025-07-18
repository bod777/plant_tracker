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

const TaxonomyChart: React.FC<TaxonomyChartProps> = ({ taxonomy }) => {
  const entries = LEVEL_ORDER
    .filter((level) => taxonomy[level])
    .map((level) => ({ level, value: taxonomy[level] }));

  if (entries.length === 0) return null;

  return (
    <ul className="relative border-l-2 border-green-600 pl-4 space-y-2">
      {entries.map(({ level, value }) => (
        <li key={level} className="relative pl-2">
          <span className="absolute -left-3 top-2 w-2 h-2 bg-green-600 rounded-full"></span>
          <span className="capitalize font-semibold mr-1">{level}:</span>
          <span className="italic text-gray-700">{value}</span>
        </li>
      ))}
    </ul>
  );
};

export default TaxonomyChart;
