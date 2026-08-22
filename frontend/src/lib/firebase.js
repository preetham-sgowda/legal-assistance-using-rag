import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyC7PM5wZreUfFUp9q8jmDZVyf_J67ywY4I",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "legal-assistance-using-rag.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "legal-assistance-using-rag",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "legal-assistance-using-rag.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "104811261184",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:104811261184:web:18d989424b875a43ab57e5",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
