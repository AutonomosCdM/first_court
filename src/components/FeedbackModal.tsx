import React, { useState } from 'react';
import { getFirestore, collection, addDoc, Timestamp } from 'firebase/firestore';
import { app } from '../firebase.app.config';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({ isOpen, onClose }) => {
  const [feedbackType, setFeedbackType] = useState<'bug' | 'suggestion' | 'other'>('suggestion');
  const [feedbackText, setFeedbackText] = useState('');
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const db = getFirestore(app);
      await addDoc(collection(db, 'user_feedback'), {
        type: feedbackType,
        message: feedbackText,
        email: email || 'Anonymous',
        timestamp: Timestamp.now(),
        appVersion: import.meta.env.PACKAGE_VERSION || 'unknown'
      });

      setSubmitStatus('success');
      setFeedbackText('');
      setEmail('');
      
      // Auto-close after successful submission
      setTimeout(() => {
        onClose();
        setSubmitStatus('idle');
      }, 2000);
    } catch (error) {
      console.error('Feedback submission error:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl w-96">
        <h2 className="text-xl font-bold mb-4">Provide Feedback</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Feedback Type</label>
            <select 
              value={feedbackType} 
              onChange={(e) => setFeedbackType(e.target.value as 'bug' | 'suggestion' | 'other')}
              className="w-full p-2 border rounded"
            >
              <option value="suggestion">Suggestion</option>
              <option value="bug">Bug Report</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Your Feedback</label>
            <textarea 
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              className="w-full p-2 border rounded h-24"
              placeholder="Share your thoughts..."
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Email (Optional)</label>
            <input 
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="Your email (optional)"
            />
          </div>
          <div className="flex justify-between">
            <button 
              type="button"
              onClick={onClose}
              className="bg-gray-200 text-gray-800 px-4 py-2 rounded"
            >
              Cancel
            </button>
            <button 
              type="submit"
              disabled={isSubmitting}
              className={`px-4 py-2 rounded ${
                isSubmitting 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
          {submitStatus === 'success' && (
            <div className="mt-4 text-green-600 text-center">
              Feedback submitted successfully!
            </div>
          )}
          {submitStatus === 'error' && (
            <div className="mt-4 text-red-600 text-center">
              Failed to submit feedback. Please try again.
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default FeedbackModal;
