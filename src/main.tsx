import React, { useState } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import FeedbackModal from './components/FeedbackModal'
import './index.css'

function RootComponent() {
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  return (
    <React.StrictMode>
      <App />
      <div className="fixed bottom-4 right-4 z-50">
        <button 
          onClick={() => setIsFeedbackOpen(true)}
          className="bg-blue-500 text-white px-4 py-2 rounded-full shadow-lg hover:bg-blue-600 transition-colors"
        >
          Feedback
        </button>
        <FeedbackModal 
          isOpen={isFeedbackOpen} 
          onClose={() => setIsFeedbackOpen(false)} 
        />
      </div>
    </React.StrictMode>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <RootComponent />
);
