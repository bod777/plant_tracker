import React, { useState, useEffect } from 'react';
import { Camera, Upload, History, Leaf } from 'lucide-react';
import PlantCamera from '@/components/PlantCamera';
import ImageUpload from '@/components/ImageUpload';
import PlantResult from '@/components/PlantResult';
import HistorySection from '@/components/HistorySection';
import AuthButton from '@/components/AuthButton';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { identifyPlant, fetchPlants, deletePlant, API_BASE } from '../api/api';
import { IdentifiedPlant } from '../api/models';
import { useGeolocation } from '@/hooks/use-location';
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { toast } from '@/hooks/use-toast';

const Index = () => {
  const [user, setUser] = useState<{ email: string } | null>(null);
  const [authLoading, setAuthLoading] = useState(true);

  const [currentResult, setCurrentResult] = useState<IdentifiedPlant | null>(null);
  const [identificationHistory, setIdentificationHistory] = useState<IdentifiedPlant[]>([]);
  const { latitude, longitude } = useGeolocation();
  const [isLoading, setIsLoading] = useState(true);
  const [identifying, setIdentifying] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

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

  // After authentication, replace the OAuth callback route with the home page
  // in browser history. Only run once so normal navigation isn't affected.
  const [didReplaceAuthRoute, setDidReplaceAuthRoute] = useState(false);
  useEffect(() => {
    if (!didReplaceAuthRoute && !authLoading && user) {
      navigate('/', { replace: true });
      setDidReplaceAuthRoute(true);
    }
  }, [didReplaceAuthRoute, authLoading, user, navigate]);

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
        toast({ description: 'Could not load previous identifications.' });
      } finally {
        setIsLoading(false);
      }
    })();
  }, [user]);

  const handleImageCapture = async (images: string[]) => {
    setIdentifying(true);
    try {
      const resp = await identifyPlant(
        images,
        latitude ?? undefined,
        longitude ?? undefined
      );

      if (!resp) {
        alert(
          'Failed to identify plant. Try taking more photos. Tips: https://plant.id/collection/xQQUmUFTkdZp1iI'
        );
        return;
      }

      setCurrentResult(resp);
      setIdentificationHistory(prev => [resp, ...prev]);
      navigate('/result');
    } catch (e) {
      console.error(e);
      toast({ description: 'Failed to identify plant.' });
    } finally {
      setIdentifying(false);
    }
  };

  const handleImageUpload = handleImageCapture;

  const handleDeletePlant = async (id: string) => {
    try {
      await deletePlant(id);
      setIdentificationHistory(prev => prev.filter(p => p.id !== id));
    } catch (e) {
      console.error(e);
      alert(
        'Failed to identify plant. Try taking more photos. Tips: https://plant.id/collection/xQQUmUFTkdZp1iI'
      );
    } finally {
      setIdentifying(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
        <div className="container mx-auto px-4 py-6 md:py-8 text-center">
          <Leaf className="h-8 w-8 text-green-600 animate-pulse mx-auto" />
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center space-y-6 py-16 bg-gradient-to-br from-green-50 to-blue-50">
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

  const Home = () => {
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
        <div className="flex justify-between items-center mb-6 md:mb-8">
          <div className="flex items-center">
            <Leaf className="h-8 w-8 text-green-600 mr-2" />
            <h1 className="text-4xl font-bold text-gray-800">Plant Tracker</h1>
          </div>
          <AuthButton />
        </div>

        <div className="space-y-6 md:space-y-8">
          <div className="text-center space-y-4">
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Identify plants instantly using your camera or by uploading photos. Discover the botanical world around you!
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-4 md:gap-6 max-w-4xl mx-auto">
            <Card
              className="p-6 md:p-8 hover:shadow-lg transition-shadow cursor-pointer group"
              onClick={() => navigate('/camera')}
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
              className="p-6 md:p-8 hover:shadow-lg transition-shadow cursor-pointer group"
              onClick={() => navigate('/upload')}
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
                onClick={() => navigate('/history')}
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
  };

  return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
        <div className="container mx-auto px-4 py-6 md:py-8">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Home />} />
          <Route
            path="/camera"
            element={<PlantCamera identifying={identifying} onCapture={handleImageCapture} onBack={() => navigate('/')} />}
          />
          <Route
            path="/upload"
            element={<ImageUpload identifying={identifying} onUpload={handleImageUpload} onBack={() => navigate('/')} />}
          />
          <Route
            path="/result"
            element={
              <PlantResult
                result={currentResult}
                identifying={identifying}
                onBack={() => navigate('/')}
                onViewHistory={() => navigate('/history')}
              />
            }
          />
          <Route
            path="/history"
            element={
              <HistorySection
                history={identificationHistory}
                onBack={() => navigate('/')}
                onSelectResult={(result) => {
                  setCurrentResult(result);
                  navigate('/result');
                }}
                onDelete={handleDeletePlant}
              />
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
};

export default Index;
