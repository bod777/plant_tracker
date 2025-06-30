// src/components/AuthButton.tsx
import React, { useEffect, useState } from 'react';
import { API_BASE } from '../api/api';

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
      <button onClick={() => {
        // logging out just clears the cookie
        fetch(`${API_BASE}/api/auth/logout`, {
          method: 'POST',
          credentials: 'include'
        }).then(() => window.location.reload());
      }}>
        Sign out ({user.email})
      </button>
    );
  }

  return (
    <button onClick={() => {
      // Redirect to your FastAPI Google login endpoint:
      window.location.href = `${API_BASE}/api/auth/google/login`;
    }}>
      Sign in with Google
    </button>
  );
}
