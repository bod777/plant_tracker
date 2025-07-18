
import React from 'react';
import { ArrowLeft, Calendar, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from '@/components/ui/select';
import { IdentifiedPlant } from '@/api/models';
import PlantCard from './PlantCard';

interface HistorySectionProps {
  history: IdentifiedPlant[];
  onBack: () => void;
  onSelectResult: (result: IdentifiedPlant) => void;
  onDelete?: (id: string) => void;
}

const HistorySection: React.FC<HistorySectionProps> = ({ history, onBack, onSelectResult, onDelete }) => {
  const [searchTerm, setSearchTerm] = React.useState('');
  const [sortOption, setSortOption] = React.useState<'newest' | 'oldest' | 'nameAsc' | 'nameDesc'>('newest');

  const filteredHistory = history.filter(item =>
    item.plantName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.scientificName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedHistory = [...filteredHistory].sort((a, b) => {
    switch (sortOption) {
      case 'nameAsc':
        return a.plantName.localeCompare(b.plantName);
      case 'nameDesc':
        return b.plantName.localeCompare(a.plantName);
      case 'oldest':
        return a.timestamp.getTime() - b.timestamp.getTime();
      case 'newest':
      default:
        return b.timestamp.getTime() - a.timestamp.getTime();
    }
  });

  const groupedHistory = (sortOption === 'newest' || sortOption === 'oldest')
    ? sortedHistory.reduce((groups, item) => {
        const date = item.timestamp.toDateString();
        if (!groups[date]) {
          groups[date] = [];
        }
        groups[date].push(item);
        return groups;
      }, {} as Record<string, IdentifiedPlant[]>)
    : { all: sortedHistory } as Record<string, IdentifiedPlant[]>;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Button onClick={onBack} variant="outline" size="lg">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <h2 className="text-2xl font-bold text-gray-800">Identification History</h2>
        <div className="w-24"></div>
      </div>

      {/* Search */}
      <Card className="p-4 space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search plants..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="max-w-xs">
          <Select value={sortOption} onValueChange={value => setSortOption(value as 'newest' | 'oldest' | 'nameAsc' | 'nameDesc')}>
            <SelectTrigger>
              <SelectValue placeholder="Sort" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="newest">Newest</SelectItem>
              <SelectItem value="oldest">Oldest</SelectItem>
              <SelectItem value="nameAsc">Name (A-Z)</SelectItem>
              <SelectItem value="nameDesc">Name (Z-A)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </Card>

      {/* History */}
      {Object.keys(groupedHistory).length === 0 ? (
        <Card className="p-12 text-center">
          <div className="space-y-4">
            <div className="text-gray-500 text-lg">
              {searchTerm ? 'No plants found matching your search' : 'No plant identifications yet'}
            </div>
            <p className="text-gray-400">
              {searchTerm ? 'Try adjusting your search terms' : 'Start identifying plants to see your history here'}
            </p>
          </div>
        </Card>
      ) : (sortOption === 'newest' || sortOption === 'oldest') ? (
        <div className="space-y-8">
          {Object.entries(groupedHistory)
            .sort(([a], [b]) =>
              sortOption === 'oldest'
                ? new Date(a).getTime() - new Date(b).getTime()
                : new Date(b).getTime() - new Date(a).getTime()
            )
            .map(([date, items]) => (
              <div key={date} className="space-y-4">
                <div className="flex items-center space-x-2 text-gray-600">
                  <Calendar className="h-4 w-4" />
                  <h3 className="font-semibold">{date}</h3>
                  <span className="text-sm">({items.length} identification{items.length !== 1 ? 's' : ''})</span>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {items.map((item) => (
                    <PlantCard
                      key={item.id}
                      plant={item}
                      onClick={() => onSelectResult(item)}
                      onDelete={onDelete}
                    />
                  ))}
                </div>
              </div>
            ))}
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {groupedHistory.all.map((item) => (
            <PlantCard
              key={item.id}
              plant={item}
              onClick={() => onSelectResult(item)}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}

      {/* Stats */}
      {history.length > 0 && (
        <Card className="p-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">Your Plant Journey</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-green-600">{history.length}</div>
              <div className="text-sm text-gray-600">Plants Identified</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {new Set(history.map(h => h.plantName)).size}
              </div>
              <div className="text-sm text-gray-600">Unique Species</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(history.reduce((sum, h) => sum + h.confidence, 0) / history.length)}%
              </div>
              <div className="text-sm text-gray-600">Avg. Confidence</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {Math.max(...history.map(h => h.confidence)).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Best Match</div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default HistorySection;
