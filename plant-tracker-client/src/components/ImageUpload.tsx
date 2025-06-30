
import React, { useRef, useState } from 'react';
import { Upload, X, Image } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface ImageUploadProps {
  onUpload: (imageData: string) => void;
  onBack: () => void;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onUpload, onBack }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const imageData = e.target?.result as string;
      setPreview(imageData);
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

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (preview) {
      onUpload(preview);
    }
  };

  const clearPreview = () => {
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Button onClick={onBack} variant="outline" size="lg">
          <X className="mr-2 h-4 w-4" />
          Back
        </Button>
        <h2 className="text-2xl font-bold text-gray-800">Upload Image</h2>
        <div></div>
      </div>

      <Card className="p-8">
        {!preview ? (
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
            <div className="relative">
              <img
                src={preview}
                alt="Plant preview"
                className="w-full max-h-96 object-contain rounded-lg"
              />
              <Button
                onClick={clearPreview}
                variant="outline"
                size="sm"
                className="absolute top-4 right-4 bg-white"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex justify-center space-x-4">
              <Button onClick={clearPreview} variant="outline">
                Choose Different Image
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
