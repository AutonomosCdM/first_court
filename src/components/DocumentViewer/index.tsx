import React, { useEffect, useRef, useState } from 'react';
import { useTheme } from '@mui/material';
import { DocumentToolbar } from './DocumentToolbar';
import { LoadingIndicator } from '../common/LoadingIndicator';
import { useDocumentState } from '../../hooks/useDocumentState';
import { useDocumentSync } from '../../hooks/useDocumentSync';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';

interface DocumentViewerProps {
  documentId: string;
  initialPage?: number;
  showToolbar?: boolean;
  onStateChange?: (state: DocumentState) => void;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  documentId,
  initialPage = 1,
  showToolbar = true,
  onStateChange
}) => {
  const theme = useTheme();
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Estado del documento
  const {
    currentPage,
    totalPages,
    zoom,
    isOffline,
    setCurrentPage,
    setZoom,
    setOffline
  } = useDocumentState(documentId, initialPage);

  // Sincronización en tiempo real
  const {
    collaborators,
    cursors,
    syncState,
    sendCursorPosition,
    sendDocumentUpdate
  } = useDocumentSync(documentId);

  // Atajos de teclado
  useKeyboardShortcuts({
    'ctrl+plus': () => setZoom(zoom + 0.1),
    'ctrl+minus': () => setZoom(zoom - 0.1),
    'ctrl+0': () => setZoom(1),
    'pageup': () => setCurrentPage(Math.max(1, currentPage - 1)),
    'pagedown': () => setCurrentPage(Math.min(totalPages, currentPage + 1))
  });

  // Cargar documento
  useEffect(() => {
    const loadDocument = async () => {
      try {
        setIsLoading(true);
        // Integración con Google Docs
        const iframe = iframeRef.current;
        if (iframe) {
          iframe.src = `https://docs.google.com/document/d/${documentId}/edit?rm=minimal`;
          
          // Escuchar eventos de carga
          iframe.onload = () => {
            setIsLoading(false);
            // Inicializar observadores y sincronización
            initializeViewerSync(iframe);
          };
        }
      } catch (err) {
        setError(err.message);
        setIsLoading(false);
      }
    };

    loadDocument();
  }, [documentId]);

  // Inicializar sincronización del visor
  const initializeViewerSync = (iframe: HTMLIFrameElement) => {
    // Observar cambios en el documento
    const observer = new MutationObserver((mutations) => {
      // Enviar actualizaciones a otros colaboradores
      sendDocumentUpdate(mutations);
    });

    // Observar movimiento del cursor
    iframe.contentWindow?.addEventListener('mousemove', (e) => {
      sendCursorPosition({
        x: e.clientX,
        y: e.clientY,
        page: currentPage
      });
    });
  };

  // Renderizar cursores de colaboradores
  const renderCollaboratorCursors = () => {
    return cursors.map((cursor) => (
      <div
        key={cursor.userId}
        style={{
          position: 'absolute',
          left: cursor.x,
          top: cursor.y,
          width: 20,
          height: 20,
          pointerEvents: 'none',
          transition: 'all 0.1s ease'
        }}
      >
        <div
          style={{
            width: 10,
            height: 10,
            borderRadius: '50%',
            backgroundColor: cursor.color
          }}
        />
        <span style={{ marginLeft: 15, fontSize: 12 }}>
          {cursor.userName}
        </span>
      </div>
    ));
  };

  if (error) {
    return (
      <div className="error-container">
        <h3>Error al cargar el documento</h3>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div
      className="document-viewer"
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        backgroundColor: theme.palette.background.paper
      }}
    >
      {showToolbar && (
        <DocumentToolbar
          currentPage={currentPage}
          totalPages={totalPages}
          zoom={zoom}
          isOffline={isOffline}
          collaborators={collaborators}
          onPageChange={setCurrentPage}
          onZoomChange={setZoom}
          onOfflineToggle={setOffline}
        />
      )}

      <div
        className="document-container"
        style={{
          position: 'relative',
          width: '100%',
          height: 'calc(100% - 64px)', // Altura total menos toolbar
          overflow: 'hidden'
        }}
      >
        {isLoading && <LoadingIndicator />}
        
        <iframe
          ref={iframeRef}
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
            transform: `scale(${zoom})`,
            transformOrigin: 'top left'
          }}
          title="Document Viewer"
        />

        {renderCollaboratorCursors()}
      </div>
    </div>
  );
};
