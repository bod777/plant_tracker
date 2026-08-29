
import React from 'react';
import { Clock, Award, Trash } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { IdentifiedPlant } from '@/api/models';
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from '@/components/ui/alert-dialog';

interface PlantCardProps {
  plant: IdentifiedPlant;
  onClick: () => void;
  onDelete?: (id: string) => void;
}

const PlantCard: React.FC<PlantCardProps> = ({ plant, onClick, onDelete }) => {
  const confidenceClasses = plant.confidence >= 90
    ? 'bg-success text-success-foreground'
    : plant.confidence >= 70
    ? 'bg-warning text-warning-foreground'
    : 'bg-destructive text-destructive-foreground';

  return (
    <Card
      role="button"
      tabIndex={0}
      aria-label={`View details for ${plant.plantName}`}
      className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
    >
      <div className="relative">
        <img
          src={plant.image_urls[0]}
          alt={plant.plantName}
          loading="lazy"
          className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
        />
        {onDelete && (
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <button
                type="button"
                aria-label="Delete plant record"
                className="absolute top-2 left-2 h-11 w-11 flex items-center justify-center bg-destructive/75 text-destructive-foreground rounded-full hover:bg-destructive focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                onClick={(e) => e.stopPropagation()}
                onKeyDown={(e) => e.stopPropagation()}
              >
                <Trash className="h-4 w-4" />
              </button>
            </AlertDialogTrigger>
            <AlertDialogContent onClick={(e) => e.stopPropagation()}>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete record?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={() => onDelete(plant.id)}>
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        )}
        <Badge
          variant="outline"
          className={`absolute top-2 right-2 ${confidenceClasses} border-none`}
        >
          <Award className="mr-1 h-3 w-3" />
          {plant.confidence.toFixed(0)}%
        </Badge>
      </div>
      
      <div className="p-4 space-y-2">
        <h3 className="font-semibold text-foreground truncate">
          {plant.plantName}
        </h3>
        <p className="text-sm text-muted-foreground italic truncate">
          {plant.scientificName}
        </p>

        <div className="flex items-center justify-between text-xs text-muted-foreground">
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
