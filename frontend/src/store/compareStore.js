import { create } from 'zustand'

const useCompareStore = create((set) => ({
  sessionA: null,
  sessionB: null,
  statusA: 'idle',
  statusB: 'idle',
  graphDataA: null,
  graphDataB: null,
  errorA: null,
  errorB: null,
  filenameA: '',
  filenameB: '',
  syncFilters: false,

  setSessionA: (sessionA) => set({ sessionA }),
  setSessionB: (sessionB) => set({ sessionB }),
  setStatusA: (statusA) => set({ statusA }),
  setStatusB: (statusB) => set({ statusB }),
  setGraphDataA: (graphDataA) => set({ graphDataA }),
  setGraphDataB: (graphDataB) => set({ graphDataB }),
  setErrorA: (errorA) => set({ errorA, statusA: 'error' }),
  setErrorB: (errorB) => set({ errorB, statusB: 'error' }),
  setFilenameA: (filenameA) => set({ filenameA }),
  setFilenameB: (filenameB) => set({ filenameB }),
  toggleSyncFilters: () => set((state) => ({ syncFilters: !state.syncFilters })),
  reset: () => set({
    sessionA: null, sessionB: null,
    statusA: 'idle', statusB: 'idle',
    graphDataA: null, graphDataB: null,
    errorA: null, errorB: null,
    filenameA: '', filenameB: '',
    syncFilters: false,
  }),
}))

export default useCompareStore