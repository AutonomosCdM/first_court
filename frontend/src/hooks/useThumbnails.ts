import { useState, useEffect } from 'react';
import { getThumbnails } from '@/api/documents';

interface Thumbnail {
  pageNumber: number;
  url: string;
}

export const useThumbnails = (documentId: string) => {
  const [thumbnails, setThumbnails] = useState<Thumbnail[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchThumbnails = async () => {
      try {
        setIsLoading(true);
        const response = await getThumbnails(documentId);
        setThumbnails(response.thumbnails);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch thumbnails'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchThumbnails();
  }, [documentId]);

  return {
    thumbnails,
    isLoading,
    error,
  };
};

export default useThumbnails;
