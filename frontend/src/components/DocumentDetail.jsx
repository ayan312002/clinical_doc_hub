import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Trash2, RefreshCw, Clock, AlertTriangle,
  CheckCircle, Loader, FileText, Activity, Download
} from 'lucide-react'
import { getDocument, deleteDocument, reprocessDocument } from '../api/client'
import ExtractionCard from './ExtractionCard'
import SummaryPanel from './SummaryPanel'

const triageColors = {
  critical: 'bg-red-100 text-red-800',
  high: 'bg-orange-100 text-orange-800',
  routine: 'bg-blue-100 text-blue-800',
  normal: 'bg-green-100 text-green-800',
}

const statusConfig = {
  uploaded: { icon: Clock, color: 'text-gray-400', label: 'Uploaded' },
  processing: { icon: Loader, color: 'text-yellow-500', label: 'Processing', spin: true },
  completed: { icon: CheckCircle, color: 'text-green-500', label: 'Completed' },
  failed: { icon: AlertTriangle, color: 'text-red-500', label: 'Failed' },
}

const imageExts = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff']
const pdfExts = ['.pdf']
const docxExts = ['.docx']
const textExts = ['.txt', '.md']

function getExt(filename) {
  return filename.toLowerCase().split('.').pop()
}

function isImage(filename) {
  return imageExts.some(ext => filename.toLowerCase().endsWith(ext))
}
function isPdf(filename) {
  return pdfExts.some(ext => filename.toLowerCase().endsWith(ext))
}
function isDocx(filename) {
  return docxExts.some(ext => filename.toLowerCase().endsWith(ext))
}
function isText(filename) {
  return textExts.some(ext => filename.toLowerCase().endsWith(ext))
}

function DocxPreview({ documentId }) {
  const containerRef = useRef(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function render() {
      try {
        const { renderAsync } = await import('docx-preview')
        const resp = await fetch(`/api/documents/${documentId}/file`)
        if (!resp.ok) throw new Error('Failed to fetch file')
        const blob = await resp.blob()
        const buffer = await blob.arrayBuffer()
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = ''
          await renderAsync(buffer, containerRef.current, undefined, {
            className: 'docx-preview',
          })
        }
      } catch (e) {
        if (!cancelled) setError(e.message)
      }
    }
    render()
    return () => { cancelled = true }
  }, [documentId])

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
        <p className="text-gray-600 mb-3">Could not render DOCX preview</p>
        <p className="text-sm text-gray-400 mb-4">{error}</p>
        <a href={`/api/documents/${documentId}/file`} download
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-clinical-600 text-white rounded-lg hover:bg-clinical-700">
          <Download className="h-4 w-4" /> Download File
        </a>
      </div>
    )
  }

  return <div ref={containerRef} className="docx-container p-4 overflow-auto max-h-[800px]" />
}

function TextViewer({ documentId, filename }) {
  const [text, setText] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`/api/documents/${documentId}/file`)
      .then(r => { if (!r.ok) throw new Error('Failed'); return r.text() })
      .then(setText)
      .catch(e => setError(e.message))
  }, [documentId])

  if (error) return <p className="text-red-500 text-center py-8">{error}</p>
  if (text === null) return <div className="text-center py-8"><Loader className="h-6 w-6 animate-spin mx-auto text-gray-400" /></div>

  return (
    <pre className="p-4 text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed overflow-auto max-h-[800px]">
      {text}
    </pre>
  )
}

export default function DocumentDetail({ doc }) {
  const [activeTab, setActiveTab] = useState('extraction')
  const status = statusConfig[doc.status] || statusConfig.uploaded
  const StatusIcon = status.icon

  const tabs = [
    { id: 'extraction', label: 'Extracted Data' },
    { id: 'summary', label: 'AI Summary' },
    { id: 'raw', label: 'Raw Text' },
    { id: 'document', label: 'Document' },
  ]

  function renderDocumentPreview() {
    if (isPdf(doc.filename)) {
      return (
        <iframe
          src={`/api/documents/${doc.id}/file`}
          className="w-full h-[800px] border-0 rounded"
          title={doc.filename}
        />
      )
    }
    if (isImage(doc.filename)) {
      return (
        <img
          src={`/api/documents/${doc.id}/file`}
          alt={doc.filename}
          className="max-w-full mx-auto rounded"
        />
      )
    }
    if (isDocx(doc.filename)) {
      return <DocxPreview documentId={doc.id} />
    }
    if (isText(doc.filename)) {
      return <TextViewer documentId={doc.id} filename={doc.filename} />
    }
    return (
      <div className="text-center py-12">
        <FileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500 mb-3">Preview not available for this file type</p>
        <a
          href={`/api/documents/${doc.id}/file`}
          download
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-clinical-600 text-white rounded-lg hover:bg-clinical-700 transition-colors"
        >
          <Download className="h-4 w-4" />
          Download File
        </a>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{doc.filename}</h2>
            <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <StatusIcon className={`h-4 w-4 ${status.color} ${status.spin ? 'animate-spin' : ''}`} />
                {status.label}
              </span>
              {doc.triage_level && (
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${triageColors[doc.triage_level]}`}>
                  {doc.triage_level.toUpperCase()}
                </span>
              )}
              {doc.patient_mrn && (
                <span className="text-gray-400">MRN: {doc.patient_mrn}</span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="border-b border-gray-200">
        <nav className="flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-clinical-500 text-clinical-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {activeTab === 'extraction' && doc.extraction && (
        <ExtractionCard extraction={doc.extraction} />
      )}
      {activeTab === 'extraction' && !doc.extraction && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
          <p className="text-yellow-800">
            {doc.status === 'processing' ? 'Document is still being processed...' : 'No extraction data available'}
          </p>
        </div>
      )}
      {activeTab === 'summary' && doc.extraction && (
        <SummaryPanel extraction={doc.extraction} />
      )}
      {activeTab === 'summary' && !doc.extraction && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
          <p className="text-yellow-800">No summary available</p>
        </div>
      )}
      {activeTab === 'raw' && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
            {doc.raw_text || 'No text extracted'}
          </pre>
        </div>
      )}
      {activeTab === 'document' && (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-gray-100 flex items-center justify-between">
            <span className="text-sm text-gray-500">{doc.filename}</span>
            <a
              href={`/api/documents/${doc.id}/file`}
              download
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-clinical-600 hover:bg-clinical-50 rounded-lg transition-colors"
            >
              <Download className="h-4 w-4" />
              Download
            </a>
          </div>
          <div className="p-2">
            {renderDocumentPreview()}
          </div>
        </div>
      )}
    </div>
  )
}
