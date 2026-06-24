import { create } from 'zustand'

const useGraphStore = create((set) => ({
  status: 'idle', // idle | uploading | alias_review | graph_ready | error
  sessionId: null,
  characterList: [],
  graphData: null,
  sentimentArcs: null,
  error: null,

  setStatus: (status) => set({ status }),
  setSessionId: (sessionId) => set({ sessionId }),
  setCharacterList: (characterList) => set({ characterList }),
  setGraphData: (graphData) => set({ graphData }),
  setSentimentArcs: (sentimentArcs) => set({ sentimentArcs }),
  setError: (error) => set({ error, status: 'error' }),
  reset: () => set({
    status: 'idle',
    sessionId: null,
    characterList: [],
    graphData: null,
    sentimentArcs: null,
    error: null,
  }),
}))

export default useGraphStore