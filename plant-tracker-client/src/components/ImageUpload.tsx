
import React, { useRef, useState } from 'react';
import { Upload, X, Image } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from '@/hooks/use-toast';

interface ImageUploadProps {
  onUpload: (images: { file: File; organ: string }[]) => void;
  onBack: () => void;
  identifying?: boolean;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onUpload, onBack, identifying }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [previews, setPreviews] = useState<{ file: File; preview: string; organ: string }[]>([]);

  const handleFile = (file: File) => {
    if (previews.length >= 5) {
      toast({ description: 'You can upload up to 5 images.' });
      return;
    }
    if (!file.type.startsWith('image/')) {
      toast({ description: 'Please select an image file' });
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const imageData = e.target?.result as string;
      setPreviews(prev => [...prev, { file, preview: imageData, organ: 'auto' }]);
    };
    reader.readAsDataURL(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files) {
      Array.from(e.dataTransfer.files).forEach(handleFile);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      Array.from(e.target.files).forEach(handleFile);
    }
  };

  const handleUpload = () => {
    if (previews.length) {
      onUpload(previews.map(p => ({ file: p.file, organ: p.organ })));
    }
  };

  const clearPreview = (idx?: number) => {
    if (idx === undefined) {
      setPreviews([]);
    } else {
      setPreviews(prev => prev.filter((_, i) => i !== idx));
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

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
          <X className="mr-2 h-4 w-4" />
          Back
        </Button>
        <h2 className="text-2xl font-bold text-gray-800">Upload Image</h2>
        <div></div>
      </div>

      <Card className="p-8">
        {previews.length === 0 ? (
          <div
            className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive
                ? 'border-green-500 bg-green-50'
                : 'border-gray-300 hover:border-green-400 hover:bg-green-50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileInput}
              className="absolute inset-0 opacity-0 cursor-pointer"
            />
            
            <div className="space-y-4">
              <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                <Upload className="h-8 w-8 text-green-600" />
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  Drop your plant image here
                </h3>
                <p className="text-gray-600 mb-4">
                  or click to browse from your device
                </p>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Image className="mr-2 h-4 w-4" />
                  Choose Image
                </Button>
              </div>
              
              <p className="text-sm text-gray-500">
                Supports: JPG, PNG, GIF (max 10MB)
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {previews.map((p, idx) => (
                <div key={idx} className="relative space-y-2">
                  <img
                    src={p.preview}
                    alt={`preview-${idx}`}
                    className="w-full h-40 object-cover rounded-lg"
                  />
                  <div className="flex items-center space-x-2">
                    <Select value={p.organ} onValueChange={val => setPreviews(prev => prev.map((img,i)=> i===idx ? { ...img, organ: val } : img))}>
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="leaf">leaf</SelectItem>
                        <SelectItem value="flower">flower</SelectItem>
                        <SelectItem value="fruit">fruit</SelectItem>
                        <SelectItem value="bark">bark</SelectItem>
                        <SelectItem value="auto">auto</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button
                      onClick={() => clearPreview(idx)}
                      variant="outline"
                      size="sm"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
              {previews.length < 5 && (
                <div className="flex items-center justify-center border-2 border-dashed rounded-lg cursor-pointer" onClick={() => fileInputRef.current?.click()}>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileInput}
                    className="hidden"
                  />
                  <Upload className="h-8 w-8 text-gray-400" />
                </div>
              )}
            </div>

            <div className="flex justify-center space-x-4">
              <Button onClick={() => clearPreview()} variant="outline">
                Clear All
              </Button>
              <Button onClick={handleUpload} className="bg-green-600 hover:bg-green-700">
                Identify Plant
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default ImageUpload;
