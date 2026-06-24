import client from './client'

export async function uploadScript(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await client.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function getGraph(sessionId) {
  const response = await client.get(`/graph/${sessionId}`)
  return response.data
}

export async function mergeAliases(sessionId, merges) {
  const response = await client.post('/merge', {
    session_id: sessionId,
    merges,
  })
  return response.data
}

export async function uploadCompare(fileA, fileB) {
  const formData = new FormData()
  formData.append('file_a', fileA)
  formData.append('file_b', fileB)

  const response = await client.post('/upload/compare', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}