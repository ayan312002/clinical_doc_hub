import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Trash2, RefreshCw } from 'lucide-react'
import { getDocument, deleteDocument, reprocessDocument } from '../api/client'
import DocumentDetail from '../components/DocumentDetail'

export default function DetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [doc, setDoc] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDocument(id).then(setDoc).finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (!doc) return
    if (doc.status !== 'uploaded' && doc.status !== 'processing') return

    const interval = setInterval(async () => {
      try {
        const updated = await getDocument(id)
        setDoc(updated)
      } catch {}
    }, 10000)

    return () => clearInterval(interval)
  }, [id, doc?.status])

  const handleDelete = async () => {
    if (!confirm('Delete this document?')) return
    await deleteDocument(id)
    navigate('/')
  }

  const handleReprocess = async () => {
    await reprocessDocument(id)
    const updated = await getDocument(id)
    setDoc(updated)
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="h-8 w-8 border-2 border-clinical-500 border-t-transparent rounded-full animate-spin mx-auto" />
      </div>
    )
  }

  if (!doc) {
    return <div className="text-center py-12 text-gray-500">Document not found</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg text-gray-600"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex-1" />
        <button
          onClick={handleReprocess}
          className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
        >
          <RefreshCw className="h-4 w-4" />
          Reprocess
        </button>
        <button
          onClick={handleDelete}
          className="flex items-center gap-1.5 px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg"
        >
          <Trash2 className="h-4 w-4" />
          Delete
        </button>
      </div>
      <DocumentDetail doc={doc} />
    </div>
  )
}
