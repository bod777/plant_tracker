
import React, { useRef, useState, useEffect } from 'react';
import { Camera, X, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from '@/hooks/use-toast';

interface PlantCameraProps {
  onCapture: (images: string[]) => void;
  onBack: () => void;
}

const PlantCamera: React.FC<PlantCameraProps> = ({ onCapture, onBack }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment');
  const [captures, setCaptures] = useState<string[]>([]);

  useEffect(() => {
    startCamera();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [facingMode]);

  const startCamera = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }

      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode }
      });
      
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setIsLoading(false);
    } catch (err) {
      console.error('Error accessing camera:', err);
      setError('Unable to access camera. Please ensure you have granted camera permissions.');
      setIsLoading(false);
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;
    if (captures.length >= 5) {
      toast({ description: 'You can capture up to 5 photos.' });
      return;
    }

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    setCaptures(prev => [...prev, imageData]);
  };

  const switchCamera = () => {
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
  };

  if (error) {
    return (
      <Card className="max-w-2xl mx-auto p-8 text-center">
        <div className="space-y-4">
          <div className="text-red-500 text-lg">{error}</div>
          <Button onClick={onBack} variant="outline">
            Go Back
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Button onClick={onBack} variant="outline" size="lg">
          <X className="mr-2 h-4 w-4" />
          Back
        </Button>
        <h2 className="text-2xl font-bold text-gray-800">Take Photo</h2>
        <Button onClick={switchCamera} variant="outline" size="lg">
          <RotateCcw className="mr-2 h-4 w-4" />
          Flip
        </Button>
      </div>

      <Card className="overflow-hidden">
        <div className="relative aspect-[3/4] sm:aspect-[4/3] bg-gray-900">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
              <div className="text-white text-lg">Starting camera...</div>
            </div>
          )}
          
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            style={{ display: isLoading ? 'none' : 'block' }}
          />
          
          <canvas ref={canvasRef} className="hidden" />
          
          {!isLoading && (
            <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2">
              <Button
                onClick={capturePhoto}
                size="lg"
                className="w-16 h-16 rounded-full bg-white hover:bg-gray-100 text-gray-800 border-4 border-gray-300"
              >
                <Camera className="h-8 w-8" />
              </Button>
            </div>
          )}
        </div>
      </Card>

      {captures.length > 0 && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {captures.map((img, idx) => (
                <div key={idx} className="relative">
                <img src={img} alt={`capture-${idx}`} className="w-full h-32 object-cover rounded-lg" />
                <Button
                  onClick={() => setCaptures(c => c.filter((_, i) => i !== idx))}
                  variant="outline"
                  size="sm"
                  className="absolute top-1 right-1 bg-white"
                >
                  <X className="h-3 w-3" />
                </Button>
                </div>
              ))}
            </div>
          <div className="flex justify-center space-x-4">
            <Button onClick={() => setCaptures([])} variant="outline">
              Clear All
            </Button>
            <Button onClick={() => onCapture(captures)} disabled={captures.length === 0} className="bg-green-600 hover:bg-green-700">
              Identify Plant
            </Button>
          </div>
        </div>
      )}

      <div className="text-center text-gray-600">
        <p>Position the plant in the center of the frame and tap the camera button to capture</p>
      </div>
    </div>
  );
};

export default PlantCamera;
