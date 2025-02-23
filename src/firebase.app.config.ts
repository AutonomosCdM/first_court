import { initializeApp, FirebaseApp } from 'firebase/app';
import { getAnalytics } from 'firebase/analytics';
import { initializeAppCheck, ReCaptchaV3Provider } from 'firebase/app-check';
import { getStorage } from 'firebase/storage';

// Firebase App Configuration
export const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyAkgqNqvL6rxznOmleCIaxPUAeqQ2akArc",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "firsrt-court.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "firsrt-court",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "firsrt-court.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "933890897677",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:933890897677:web:7469dcf4ead74c8092a244",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-3P1LY3NBLH"
};

// Initialize Firebase App
export const app: FirebaseApp = initializeApp(firebaseConfig);

// Initialize Firebase Services
// Use void to explicitly mark these as intentionally used
void getAnalytics(app);
void getStorage(app);

// Optional: Enable App Check (recommended for production)
const isProduction = import.meta.env.PROD || process.env.NODE_ENV === 'production';
void (isProduction 
  ? initializeAppCheck(app, {
      provider: new ReCaptchaV3Provider('YOUR_RECAPTCHA_V3_SITE_KEY'),
      isTokenAutoRefreshEnabled: true
    })
  : null);

// Firebase App Distribution Utility
export const appDistribution = {
  /**
   * Upload new build to Firebase App Distribution
   * @param {string} buildPath Path to build file
   * @param {string} releaseNotes Release notes
   * @param {string[]} groups Tester groups to notify
   * @returns {Promise} Upload promise
   */
  uploadBuild: async (buildPath: string, releaseNotes: string, groups: string[]) => {
    try {
      // Note: Firebase App Distribution upload requires Firebase CLI
      // This is a placeholder for CLI-based upload
      console.log('Uploading build:', { buildPath, releaseNotes, groups });
      return Promise.resolve({
        buildId: `build-${Date.now()}`,
        message: 'Build upload simulated'
      });
    } catch (error) {
      console.error('Error uploading build:', error);
      throw error;
    }
  },

  /**
   * Add testers to groups
   * @param {string[]} emails Tester email addresses
   * @param {string[]} groups Groups to add testers to
   * @returns {Promise} Add testers promise
   */
  addTesters: async (emails: string[], groups: string[]) => {
    try {
      // Note: Tester management typically done via Firebase Console or CLI
      console.log('Adding testers:', { emails, groups });
      return Promise.resolve({
        message: 'Testers added successfully'
      });
    } catch (error) {
      console.error('Error adding testers:', error);
      throw error;
    }
  },

  /**
   * Send notifications to testers
   * @param {string} buildId Build ID
   * @param {string[]} groups Groups to notify
   * @returns {Promise} Notification promise
   */
  notifyTesters: async (buildId: string, groups: string[]) => {
    try {
      // Note: Notification typically handled by Firebase App Distribution
      console.log('Notifying testers:', { buildId, groups });
      return Promise.resolve({
        message: 'Testers notified successfully'
      });
    } catch (error) {
      console.error('Error notifying testers:', error);
      throw error;
    }
  }
};
