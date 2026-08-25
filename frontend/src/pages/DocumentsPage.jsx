import { useState, useEffect } from 'react'
import { listDocuments } from '../api/client'
import DocumentCard from '../components/DocumentCard'
import SearchBar from '../components/SearchBar'
import { FileText, RefreshCw } from 'lucide-react'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({})

  const fetchDocs = async () => {
    setLoading(true)
    try {
      const docs = await listDocuments(filters)
      setDocuments(docs)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchDocs() }, [filters])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-500 mt-1">{documents.length} document{documents.length !== 1 ? 's' : ''}</p>
        </div>
        <button
          onClick={fetchDocs}
          className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      <SearchBar onResults={(results) => {
        if (results !== null) setDocuments(results)
        else fetchDocs()
      }} />

      <div className="flex gap-2 flex-wrap">
        {[
          { key: 'triage', options: ['critical', 'high', 'routine', 'normal'], label: 'Triage' },
          { key: 'status', options: ['uploaded', 'processing', 'completed', 'failed'], label: 'Status' },
          { key: 'doc_type', options: ['discharge_summary', 'lab_report', 'intake_form', 'physician_notes'], label: 'Type' },
        ].map(({ key, options, label }) => (
          <select
            key={key}
            onChange={(e) => setFilters((f) => ({ ...f, [key]: e.target.value || undefined }))}
            className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 bg-white"
          >
            <option value="">All {label}</option>
            {options.map((o) => (
              <option key={o} value={o}>{o.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
            ))}
          </select>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="h-8 w-8 border-2 border-clinical-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-gray-500 mt-3">Loading documents...</p>
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12 bg-white border border-gray-200 rounded-xl">
          <FileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No documents found</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <DocumentCard key={doc.id} doc={doc} />
          ))}
        </div>
      )}
    </div>
  )
}
