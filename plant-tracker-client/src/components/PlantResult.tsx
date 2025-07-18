
import React from 'react';
import { ArrowLeft, Clock, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { IdentifiedPlant } from '../api/models';
import { updatePlantNotes } from '@/api/api';
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
}

const PlantResult: React.FC<PlantResultProps> = ({ result, onBack, onViewHistory }) => {
  const [notes, setNotes] = React.useState(result?.notes || '');
  const [saving, setSaving] = React.useState(false);
  const [editing, setEditing] = React.useState(!result?.notes);
  const [showSaved, setShowSaved] = React.useState(false);

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
      alert('Failed to save notes');
    } finally {
      setSaving(false);
    }
  };
  if (!result) {
    return (
      <Card className="max-w-2xl mx-auto p-8 text-center">
        <div className="text-gray-500">No result to display</div>
        <Button onClick={onBack} variant="outline" className="mt-4">
          Go Back
        </Button>
      </Card>
    );
  }

  const confidenceColor = result.confidence >= 90 ? 'bg-green-500' : 
                          result.confidence >= 70 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Button onClick={onBack} variant="outline" size="lg">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        {/* <h2 className="text-2xl font-bold text-gray-800">Plant Identified</h2> */}
        <Button onClick={onViewHistory} variant="outline" size="lg">
          <Eye className="mr-2 h-4 w-4" />
          History
        </Button>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Image Carousel */}
        <Card className="overflow-hidden">
          <Carousel className="w-full">
            <CarouselContent>
              {[
                ...(result.image_data),
                ...(result.similar_images?.map(img => img.url) || [])
              ].map((src, idx) => (
                <CarouselItem key={idx} className="flex items-center justify-center">
                  <img
                    src={src}
                    alt={`Plant image ${idx}`}
                    className="w-full h-80 object-cover"
                  />
                </CarouselItem>
              ))}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
          </Carousel>
        </Card>

        {/* Results */}
        <Card className="p-6 space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Badge variant="outline" className={`${confidenceColor} text-white px-3 py-1`}>
                {result.confidence.toFixed(1)}% Match
              </Badge>
              <div className="flex items-center text-sm text-gray-500">
                <Clock className="mr-1 h-4 w-4" />
                {result.timestamp.toLocaleDateString()}
              </div>
            </div>

            <div>
              <h3 className="text-3xl font-bold text-gray-800 mb-2">
                {result.plantName}
              </h3>
              <p className="text-lg text-gray-600 italic">
                {result.scientificName}
              </p>
            </div>

            <div className="pt-4 border-t">
              <h4 className="font-semibold text-gray-800 mb-2">Description</h4>
              <p className="text-gray-600 leading-relaxed">
                {result.description}
              </p>
            </div>
          </div>

          <div className="flex space-x-3">
            <Button asChild className="flex-1 bg-green-600 hover:bg-green-700">
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-center py-2"
              >
                Wikipedia Page
              </a>
            </Button>

            {/* Button to Google search the plant name */}
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

      {/* Taxonomy */}
      {result.taxonomy && (
        <Card className="p-6 space-y-4">
          <h4 className="text-xl font-semibold text-gray-800">Taxonomy</h4>
          <TaxonomyChart taxonomy={result.taxonomy} />
        </Card>
      )}

      {/* Notes */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-xl font-semibold text-gray-800">Your Notes</h4>
          {showSaved && (
            <span className="text-sm text-green-600">Saved!</span>
          )}
        </div>
        {editing ? (
          <>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add notes..."
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
            <p className="whitespace-pre-wrap text-gray-700">{notes}</p>
            <Button variant="outline" onClick={() => setEditing(true)}>
              Edit
            </Button>
          </div>
        )}
      </Card>

      {/* Additional Information */}
      <Card className="p-6">
        <h4 className="text-xl font-semibold text-gray-800 mb-4">
          Plant Care Tips
        </h4>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h5 className="font-semibold text-blue-800 mb-2">Watering</h5>
            <p className="text-blue-700">{result.watering}</p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h5 className="font-semibold text-yellow-800 mb-2">Light</h5>
            <p className="text-yellow-700">{result.light_condition}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h5 className="font-semibold text-green-800 mb-2">Soil</h5>
            <p className="text-green-700">{result.soil_type}</p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default PlantResult;
