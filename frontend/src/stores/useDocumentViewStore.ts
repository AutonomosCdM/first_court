import { create } from 'zustand';

interface DocumentViewState {
  currentPage: number;
  zoom: number;
  rotation: number;
  splitView: boolean;
  preferences: {
    darkMode: boolean;
    highlightColor: string;
    fontSize: number;
  };
  setCurrentPage: (page: number) => void;
  setZoom: (zoom: number) => void;
  setRotation: (rotation: number) => void;
  toggleSplitView: () => void;
  updatePreferences: (preferences: Partial<DocumentViewState['preferences']>) => void;
}

export const useDocumentViewStore = create<DocumentViewState>((set) => ({
  currentPage: 1,
  zoom: 1,
  rotation: 0,
  splitView: false,
  preferences: {
    darkMode: false,
    highlightColor: '#ffeb3b',
    fontSize: 16,
  },
  setCurrentPage: (page) => set({ currentPage: page }),
  setZoom: (zoom) => set({ zoom }),
  setRotation: (rotation) => set({ rotation }),
  toggleSplitView: () => set((state) => ({ splitView: !state.splitView })),
  updatePreferences: (preferences) =>
    set((state) => ({
      preferences: { ...state.preferences, ...preferences },
    })),
}));

export default useDocumentViewStore;
