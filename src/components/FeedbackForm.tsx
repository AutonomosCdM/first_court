import React, { useState } from 'react';
import { getFirestore, collection, addDoc } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';

interface FeedbackFormProps {
  buildId?: string;
  version?: string;
}

interface FeedbackData {
  buildId: string;
  version: string;
  userId: string;
  userEmail: string;
  type: 'bug' | 'feature' | 'improvement';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  deviceInfo: {
    platform: string;
    userAgent: string;
    screenSize: string;
  };
  timestamp: Date;
}

/**
 * In-app feedback form component for testers
 */
export const FeedbackForm: React.FC<FeedbackFormProps> = ({ buildId, version }) => {
  const [type, setType] = useState<'bug' | 'feature' | 'improvement'>('bug');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState<'low' | 'medium' | 'high'>('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const auth = getAuth();
  const db = getFirestore();

  const getDeviceInfo = () => ({
    platform: navigator.platform,
    userAgent: navigator.userAgent,
    screenSize: `${window.innerWidth}x${window.innerHeight}`
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to submit feedback');
      }

      const feedbackData: FeedbackData = {
        buildId: buildId || 'unknown',
        version: version || 'unknown',
        userId: auth.currentUser.uid,
        userEmail: auth.currentUser.email || 'unknown',
        type,
        title,
        description,
        severity,
        deviceInfo: getDeviceInfo(),
        timestamp: new Date()
      };

      // Save to Firestore
      await addDoc(collection(db, 'feedback'), feedbackData);

      setSuccess(true);
      setTitle('');
      setDescription('');
      
      // Reset success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error submitting feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="feedback-form p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Submit Feedback</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          Feedback submitted successfully!
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-2">Type</label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value as 'bug' | 'feature' | 'improvement')}
            className="w-full p-2 border rounded"
          >
            <option value="bug">Bug Report</option>
            <option value="feature">Feature Request</option>
            <option value="improvement">Improvement Suggestion</option>
          </select>
        </div>

        <div>
          <label className="block mb-2">Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>

        <div>
          <label className="block mb-2">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-2 border rounded h-32"
            required
          />
        </div>

        {type === 'bug' && (
          <div>
            <label className="block mb-2">Severity</label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value as 'low' | 'medium' | 'high')}
              className="w-full p-2 border rounded"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className={`w-full p-2 text-white rounded ${
            isSubmitting ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'
          }`}
        >
          {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
        </button>
      </form>

      <div className="mt-4 text-sm text-gray-500">
        <p>Build: {buildId || 'unknown'}</p>
        <p>Version: {version || 'unknown'}</p>
      </div>
    </div>
  );
};
