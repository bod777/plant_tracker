
import React from 'react';
import { Clock, Award } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { PlantIdentification } from '@/pages/Index';

interface PlantCardProps {
  plant: PlantIdentification;
  onClick: () => void;
}

const PlantCard: React.FC<PlantCardProps> = ({ plant, onClick }) => {
  const confidenceColor = plant.confidence >= 90 ? 'bg-green-500' : 
                          plant.confidence >= 70 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <Card 
      className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group"
      onClick={onClick}
    >
      <div className="relative">
        <img
          src={plant.image}
          alt={plant.plantName}
          className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
        />
        <Badge 
          variant="outline" 
          className={`absolute top-2 right-2 ${confidenceColor} text-white border-none`}
        >
          <Award className="mr-1 h-3 w-3" />
          {plant.confidence.toFixed(0)}%
        </Badge>
      </div>
      
      <div className="p-4 space-y-2">
        <h3 className="font-semibold text-gray-800 truncate">
          {plant.plantName}
        </h3>
        <p className="text-sm text-gray-600 italic truncate">
          {plant.scientificName}
        </p>
        
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center">
            <Clock className="mr-1 h-3 w-3" />
            {plant.timestamp.toLocaleDateString()}
          </div>
          <div className="text-right">
            {plant.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default PlantCard;
