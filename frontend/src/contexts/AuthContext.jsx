import React, { createContext, useContext, useEffect, useState } from 'react';
import { onAuthStateChanged, signInWithPopup, signOut as firebaseSignOut } from 'firebase/auth';
import { auth, googleProvider } from '../lib/firebase';

const AuthContext = createContext({
  user: null,
  sessionToken: null,
  loading: true,
  signInWithGoogle: async () => {},
  signOut: async () => {},
});

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [sessionToken, setSessionToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      setUser(currentUser);
      if (currentUser) {
        try {
          const token = await currentUser.getIdToken();
          setSessionToken(token);
          await syncUserWithBackend(token);
        } catch (err) {
          console.warn('Failed to retrieve Firebase ID token:', err);
        }
      } else {
        setSessionToken(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const syncUserWithBackend = async (token) => {
    try {
      await fetch(`${API_URL}/auth/session`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
    } catch (err) {
      console.warn('Backend sync notice (backend server initializing or offline):', err);
    }
  };

  const signInWithGoogle = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const token = await result.user.getIdToken();
      setSessionToken(token);
      await syncUserWithBackend(token);
    } catch (error) {
      console.error('Firebase Google Auth error:', error);
      throw error;
    }
  };

  const signOut = async () => {
    await firebaseSignOut(auth);
    setUser(null);
    setSessionToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, session: { access_token: sessionToken }, loading, signInWithGoogle, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
