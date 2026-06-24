import { create } from 'zustand'

const useGraphStore = create((set, get) => ({
  status: 'idle',
  sessionId: null,
  characterList: [],
  graphData: null,
  sentimentArcs: null,
  error: null,
  activeTab: 'graph',   // 'graph' | 'sentiment'
  activeAct: 'all',     // 'all' | 1 | 2 | 3
  visibleCharacters: [],

  setStatus: (status) => set({ status }),
  setSessionId: (sessionId) => set({ sessionId }),
  setCharacterList: (characterList) => set({ characterList, visibleCharacters: characterList }),
  setGraphData: (graphData) => set({ graphData }),
  setSentimentArcs: (sentimentArcs) => set({ sentimentArcs }),
  setError: (error) => set({ error, status: 'error' }),
  setActiveTab: (activeTab) => set({ activeTab }),
  setActiveAct: (activeAct) => set({ activeAct }),
  setVisibleCharacters: (visibleCharacters) => set({ visibleCharacters }),

  reset: () => set({
    status: 'idle',
    sessionId: null,
    characterList: [],
    graphData: null,
    sentimentArcs: null,
    error: null,
    activeTab: 'graph',
    activeAct: 'all',
    visibleCharacters: [],
  }),
}))

export default useGraphStore