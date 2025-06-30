// src/components/AuthButton.tsx
import React, { useEffect, useState } from 'react';
import { API_BASE } from '../api/api';
import { Button } from '@/components/ui/button';

export default function AuthButton() {
  const [user, setUser] = useState<{ email: string } | null>(null);

  // On mount, try fetching the current user
  useEffect(() => {
    fetch(`${API_BASE}/api/auth/me`, { credentials: 'include' })
      .then(res => res.ok ? res.json() : Promise.reject())
      .then(data => setUser(data))
      .catch(() => setUser(null));
  }, []);

  if (user) {
    return (
      <Button
        onClick={() => {
          // logging out just clears the cookie
          fetch(`${API_BASE}/api/auth/logout`, {
            method: 'POST',
            credentials: 'include'
          }).then(() => window.location.reload());
        }}
        variant="outline"
        size="sm"
      >
        Sign out
      </Button>
    );
  }

  return (
    <Button
      onClick={() => {
        // Redirect to your FastAPI Google login endpoint:
        window.location.href = `${API_BASE}/api/auth/google/login`;
      }}
      className="bg-green-600 hover:bg-green-700 text-white"
    >
      Sign in with Google
    </Button>
  );
}
