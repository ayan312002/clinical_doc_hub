const API_BASE = '/api'

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`)
  return res.json()
}

export async function listDocuments(params = {}) {
  const query = new URLSearchParams()
  if (params.status) query.set('status', params.status)
  if (params.triage) query.set('triage', params.triage)
  if (params.doc_type) query.set('doc_type', params.doc_type)
  if (params.patient_mrn) query.set('patient_mrn', params.patient_mrn)
  if (params.skip) query.set('skip', params.skip)
  if (params.limit) query.set('limit', params.limit)
  const res = await fetch(`${API_BASE}/documents?${query}`)
  if (!res.ok) throw new Error('Failed to list documents')
  return res.json()
}

export async function getDocument(id) {
  const res = await fetch(`${API_BASE}/documents/${id}`)
  if (!res.ok) throw new Error('Document not found')
  return res.json()
}

export async function deleteDocument(id) {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Delete failed')
  return res.json()
}

export async function reprocessDocument(id) {
  const res = await fetch(`${API_BASE}/documents/${id}/reprocess`, { method: 'POST' })
  if (!res.ok) throw new Error('Reprocess failed')
  return res.json()
}

export async function processDocument(id) {
  const res = await fetch(`${API_BASE}/documents/${id}/process`, { method: 'POST' })
  if (!res.ok) throw new Error('Process failed')
  return res.json()
}

export async function searchDocuments(query) {
  const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`)
  if (!res.ok) throw new Error('Search failed')
  return res.json()
}

export async function listPatients() {
  const res = await fetch(`${API_BASE}/patients`)
  if (!res.ok) throw new Error('Failed to list patients')
  return res.json()
}

export async function getPatient(mrn) {
  const res = await fetch(`${API_BASE}/patients/${mrn}`)
  if (!res.ok) throw new Error('Patient not found')
  return res.json()
}

export async function getPatientDocuments(mrn) {
  const res = await fetch(`${API_BASE}/patients/${mrn}/documents`)
  if (!res.ok) throw new Error('Failed to get patient documents')
  return res.json()
}

export async function getPatientTimeline(mrn) {
  const res = await fetch(`${API_BASE}/patients/${mrn}/timeline`)
  if (!res.ok) throw new Error('Failed to get timeline')
  return res.json()
}
