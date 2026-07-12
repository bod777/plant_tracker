
import React from 'react';
import { ArrowLeft, Clock, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { IdentifiedPlant } from '../api/models';
import { updatePlantNotes } from '@/api/api';
import { toast } from '@/hooks/use-toast';
import { Textarea } from '@/components/ui/textarea';
import TaxonomyChart from './TaxonomyChart';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselPrevious,
  CarouselNext,
} from '@/components/ui/carousel';

interface PlantResultProps {
  result: IdentifiedPlant | null;
  onBack: () => void;
  onViewHistory: () => void;
  identifying?: boolean;
}

const DESCRIPTION_LIMIT = 300;

const PlantResult: React.FC<PlantResultProps> = ({ result, onBack, onViewHistory, identifying }) => {
  const [notes, setNotes] = React.useState(result?.notes || '');
  const [saving, setSaving] = React.useState(false);
  const [editing, setEditing] = React.useState(!result?.notes);
  const [showSaved, setShowSaved] = React.useState(false);
  const [descExpanded, setDescExpanded] = React.useState(false);

  React.useEffect(() => {
    setNotes(result?.notes || '');
    setEditing(!result?.notes);
  }, [result]);

  const handleSaveNotes = async () => {
    if (!result) return;
    setSaving(true);
    try {
      await updatePlantNotes({ id: result.id, notes });
      result.notes = notes;
      setEditing(false);
      setShowSaved(true);
      setTimeout(() => setShowSaved(false), 2000);
    } catch {
      toast({ description: 'Failed to save notes' });
    } finally {
      setSaving(false);
    }
  };
  if (!result) {
    return (
      <Card className="max-w-2xl mx-auto p-8 text-center">
        <div className="text-muted-foreground">No result to display</div>
        <Button onClick={onBack} variant="outline" className="mt-4">
          Go Back
        </Button>
      </Card>
    );
  }

  const confidenceClasses = result.confidence >= 90
    ? 'bg-success text-success-foreground'
    : result.confidence >= 70
    ? 'bg-warning text-warning-foreground'
    : 'bg-destructive text-destructive-foreground';

  return (
    <div className="relative max-w-4xl mx-auto space-y-6">
      {identifying && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="flex items-center space-x-2 text-white">
            <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
            <span>Identifying...</span>
          </div>
        </div>
      )}
      <div className="flex items-center justify-between">
        <Button onClick={onBack} variant="outline" size="lg">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <Button onClick={onViewHistory} variant="outline" size="lg">
          <Eye className="mr-2 h-4 w-4" />
          History
        </Button>
      </div>

      <div className="grid md:grid-cols-2 gap-8 items-start">
        {/* Image Carousel */}
        <Card className="overflow-hidden">
          <Carousel className="w-full">
            <CarouselContent>
              {[
                ...(result.image_urls || []).map((url, i) => ({
                  url,
                  alt: `Your photo ${i + 1} of ${result.plantName}`,
                })),
                ...(result.similar_images || []).map((img, i) => ({
                  url: img.url,
                  alt: `Reference image ${i + 1} of ${result.plantName} for comparison`,
                })),
              ].map(({ url, alt }, idx) => (
                <CarouselItem key={idx} className="flex items-center justify-center">
                  <img
                    src={url}
                    alt={alt}
                    loading="lazy"
                    className="w-full object-contain max-h-80 bg-muted"
                  />
                </CarouselItem>
              ))}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
          </Carousel>
        </Card>

        {/* Key info + actions */}
        <Card className="p-6 space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Badge variant="outline" className={`${confidenceClasses} px-3 py-1 border-none`}>
                {result.confidence.toFixed(1)}% Match
              </Badge>
              <div className="flex items-center text-sm text-muted-foreground">
                <Clock className="mr-1 h-4 w-4" />
                {result.timestamp.toLocaleDateString()}
              </div>
            </div>

            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                {result.plantName}
              </h1>
              <p className="text-lg text-muted-foreground italic">
                {result.scientificName}
              </p>
            </div>
          </div>

          <div className="flex space-x-3">
            <Button asChild className="flex-1">
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-center py-2"
              >
                Wikipedia Page
              </a>
            </Button>

            <Button asChild variant="outline" className="flex-1">
              <a
                href={`https://www.google.com/search?q=${encodeURIComponent(result.plantName)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-center py-2"
              >
                Search Google
              </a>
            </Button>
          </div>
        </Card>
      </div>

      {/* Description */}
      {result.description && (
        <Card className="p-6 space-y-3">
          <h2 className="font-semibold text-foreground">Description</h2>
          <p className="text-muted-foreground leading-relaxed">
            {descExpanded || result.description.length <= DESCRIPTION_LIMIT
              ? result.description
              : `${result.description.slice(0, DESCRIPTION_LIMIT).trimEnd()}…`}
          </p>
          {result.description.length > DESCRIPTION_LIMIT && (
            <button
              onClick={() => setDescExpanded(prev => !prev)}
              className="text-sm text-primary hover:underline"
            >
              {descExpanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </Card>
      )}

      {/* Taxonomy */}
      {result.taxonomy && (
        <Card className="p-6 space-y-4">
          <h2 className="text-xl font-semibold text-foreground">Taxonomy</h2>
          <TaxonomyChart taxonomy={result.taxonomy} />
        </Card>
      )}

      {/* Notes */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 id="notes-heading" className="text-xl font-semibold text-foreground">Your Notes</h2>
          {showSaved && (
            <span className="text-sm text-success">Saved!</span>
          )}
        </div>
        {editing ? (
          <>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add notes..."
              aria-labelledby="notes-heading"
            />
            <div className="flex space-x-2">
              <Button onClick={handleSaveNotes} disabled={saving}>
                {saving ? 'Saving...' : 'Save Notes'}
              </Button>
              {result.notes && (
                <Button
                  variant="outline"
                  onClick={() => {
                    setNotes(result.notes || '');
                    setEditing(false);
                  }}
                >
                  Cancel
                </Button>
              )}
            </div>
          </>
        ) : (
          <div className="space-y-2">
            <p className="whitespace-pre-wrap text-foreground">{notes}</p>
            <Button variant="outline" onClick={() => setEditing(true)}>
              Edit
            </Button>
          </div>
        )}
      </Card>

      {/* Additional Information */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4">
          Plant Care Tips
        </h2>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div className="bg-info/10 p-4 rounded-lg">
            <h3 className="font-semibold text-info mb-2">Watering</h3>
            <p className="text-foreground">{result.watering}</p>
          </div>
          <div className="bg-warning/10 p-4 rounded-lg">
            <h3 className="font-semibold text-warning mb-2">Light</h3>
            <p className="text-foreground">{result.light_condition}</p>
          </div>
          <div className="bg-success/10 p-4 rounded-lg">
            <h3 className="font-semibold text-success mb-2">Soil</h3>
            <p className="text-foreground">{result.soil_type}</p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default PlantResult;
