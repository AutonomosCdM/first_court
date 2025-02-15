import React from 'react';
import { useDocumentViewStore } from '@/stores/useDocumentViewStore';
import { useThumbnails } from '@/hooks/useThumbnails';
import ThumbnailGrid from './ThumbnailGrid';
import PreferencesPanel from './PreferencesPanel';
import CollaborationPanel from './CollaborationPanel';
import QuickActions from './QuickActions';
import SplitView from './SplitView';

interface DocumentViewerProps {
  documentId: string;
  initialPage?: number;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  documentId,
  initialPage = 1,
}) => {
  const { currentPage, zoom, setZoom } = useDocumentViewStore();
  const { thumbnails, isLoading } = useThumbnails(documentId);

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-64 border-r border-gray-200 bg-white">
        <ThumbnailGrid 
          thumbnails={thumbnails} 
          isLoading={isLoading} 
          currentPage={currentPage} 
        />
      </div>
      
      <div className="flex-1 flex flex-col">
        <QuickActions />
        
        <div className="flex-1 relative">
          <SplitView documentId={documentId} />
        </div>
        
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <PreferencesPanel />
            <CollaborationPanel documentId={documentId} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
