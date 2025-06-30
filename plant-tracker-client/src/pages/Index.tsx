import React, { useState, useEffect } from 'react';
import { Camera, Upload, History, Leaf } from 'lucide-react';
import PlantCamera from '@/components/PlantCamera';
import ImageUpload from '@/components/ImageUpload';
import PlantResult from '@/components/PlantResult';
import HistorySection from '@/components/HistorySection';
import AuthButton from '@/components/AuthButton';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { identifyPlant, fetchPlants, API_BASE } from '../api/api';
import { IdentifiedPlant } from '../api/models';

const Index = () => {
  const [user, setUser] = useState<{ email: string } | null>(null);
  const [authLoading, setAuthLoading] = useState(true);

  const [activeView, setActiveView] = useState<'home' | 'camera' | 'upload' | 'result' | 'history'>('home');
  const [currentResult, setCurrentResult] = useState<IdentifiedPlant | null>(null);
  const [identificationHistory, setIdentificationHistory] = useState<IdentifiedPlant[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Check auth on mount
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/api/auth/me`, { credentials: 'include' });
        if (res.ok) {
          const data = await res.json();
          // console.log(data);
          setUser(data);
        } else {
          setUser(null);
        }
      } catch {
        setUser(null);
      } finally {
        setAuthLoading(false);
      }
    })();
  }, []);

  // Load history after auth
  useEffect(() => {
    if (!user) return;
    (async () => {
      setIsLoading(true);
      try {
        const historyData = await fetchPlants();
        setIdentificationHistory(historyData);
      } catch (error) {
        console.error('Failed to fetch identification history:', error);
        alert('Could not load previous identifications.');
      } finally {
        setIsLoading(false);
      }
    })();
  }, [user]);

  const handleImageCapture = async (imageData: string) => {
    try {
      const resp: IdentifiedPlant = await identifyPlant(imageData, 53.282275, -6.116891);
      setCurrentResult(resp);
      setIdentificationHistory(prev => [resp, ...prev]);
      setActiveView('result');
    } catch (e) {
      console.error(e);
      alert('Failed to identify plant. Please try again.');
    }
  };

  const handleImageUpload = handleImageCapture;

  const renderContent = () => {
    if (authLoading) {
      return (
        <div className="text-center pt-16">
          <Leaf className="h-8 w-8 text-green-600 animate-pulse mx-auto" />
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      );
    }
    if (!user) {
      return (
        <div className="flex flex-col items-center justify-center text-center space-y-6 py-16">
          <div>
            <Leaf className="h-10 w-10 text-green-600 mx-auto" />
            <h1 className="text-5xl font-bold text-gray-800 mt-4">Plant Tracker</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-xl">
            Sign in with Google to identify plants from photos and keep a history of your discoveries.
          </p>
          <div>
            <AuthButton />
          </div>
        </div>
      );
    }

    switch (activeView) {
      case 'camera':
        return <PlantCamera onCapture={handleImageCapture} onBack={() => setActiveView('home')} />;
      case 'upload':
        return <ImageUpload onUpload={handleImageUpload} onBack={() => setActiveView('home')} />;
      case 'result':
        return (
          <PlantResult
            result={currentResult}
            onBack={() => setActiveView('home')}
            onViewHistory={() => setActiveView('history')}
          />
        );
      case 'history':
        return (
          <HistorySection
            history={identificationHistory}
            onBack={() => setActiveView('home')}
            onSelectResult={result => {
              setCurrentResult(result);
              setActiveView('result');
            }}
          />
        );
      default:
        if (isLoading) {
          return (
            <div className="text-center space-y-4 pt-16">
              <Leaf className="h-8 w-8 text-green-600 animate-pulse mx-auto" />
              <p className="text-xl text-gray-600">Loading your plant history...</p>
            </div>
          );
        }
        return (
          <>
            <div className="flex justify-between items-center mb-8">
              <div className="flex items-center">
                <Leaf className="h-8 w-8 text-green-600 mr-2" />
                <h1 className="text-4xl font-bold text-gray-800">Plant Tracker</h1>
              </div>
              <AuthButton />
            </div>

            <div className="space-y-8">
              <div className="text-center space-y-4">
                <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                  Identify plants instantly using your camera or by uploading photos. Discover the botanical world around you!
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                <Card
                  className="p-8 hover:shadow-lg transition-shadow cursor-pointer group"
                  onClick={() => setActiveView('camera')}
                >
                  <div className="text-center space-y-4">
                    <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center group-hover:bg-green-200 transition-colors">
                      <Camera className="h-8 w-8 text-green-600" />
                    </div>
                    <h3 className="text-2xl font-semibold text-gray-800">Take Photo</h3>
                    <p className="text-gray-600">
                      Use your device camera to capture a plant and get instant identification
                    </p>
                  </div>
                </Card>

                <Card
                  className="p-8 hover:shadow-lg transition-shadow cursor-pointer group"
                  onClick={() => setActiveView('upload')}
                >
                  <div className="text-center space-y-4">
                    <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                      <Upload className="h-8 w-8 text-blue-600" />
                    </div>
                    <h3 className="text-2xl font-semibold text-gray-800">Upload Image</h3>
                    <p className="text-gray-600">
                      Select a photo from your gallery to identify plants you've photographed before
                    </p>
                  </div>
                </Card>
              </div>

              {identificationHistory.length > 0 && (
                <div className="text-center">
                  <Button
                    onClick={() => setActiveView('history')}
                    variant="outline"
                    size="lg"
                    className="text-green-600 border-green-600 hover:bg-green-50"
                  >
                    <History className="mr-2 h-5 w-5" />
                    View History ({identificationHistory.length})
                  </Button>
                </div>
              )}
            </div>
          </>
        );
    }
  };

  return <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50"><div className="container mx-auto px-4 py-8">{renderContent()}</div></div>;
};

export default Index;
