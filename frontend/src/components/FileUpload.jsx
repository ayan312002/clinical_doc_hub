import { useState, useRef, useEffect } from 'react'
import { Upload, AlertCircle, Sparkles, X, File, FileText, Image } from 'lucide-react'
import { uploadDocument } from '../api/client'

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getFileExt(name) {
  return name.split('.').pop().toLowerCase()
}

const imageExts = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff']
const pdfExts = ['pdf']
const textExts = ['txt', 'md']

function isImage(name) { return imageExts.includes(getFileExt(name)) }
function isPdf(name) { return pdfExts.includes(getFileExt(name)) }
function isText(name) { return textExts.includes(getFileExt(name)) }

export default function FileUpload({ onUploadComplete }) {
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [textContent, setTextContent] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    if (!selectedFile) {
      setPreviewUrl(null)
      setTextContent(null)
      return
    }

    const ext = getFileExt(selectedFile.name)

    if (isPdf(selectedFile.name) || isImage(selectedFile.name)) {
      const url = URL.createObjectURL(selectedFile)
      setPreviewUrl(url)
      setTextContent(null)
      return () => URL.revokeObjectURL(url)
    }

    if (isText(selectedFile.name)) {
      const reader = new FileReader()
      reader.onload = (e) => setTextContent(e.target.result)
      reader.readAsText(selectedFile)
      setPreviewUrl(null)
      return () => reader.abort()
    }

    setPreviewUrl(null)
    setTextContent(null)
  }, [selectedFile])

  const handleFile = (file) => {
    setError(null)
    setSelectedFile(file)
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    setUploading(true)
    setError(null)
    try {
      const res = await uploadDocument(selectedFile)
      if (onUploadComplete) onUploadComplete(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setUploading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const onDragOver = (e) => {
    e.preventDefault()
    setDragOver(true)
  }

  const hasPreview = selectedFile && (previewUrl || textContent !== null)
  const ext = selectedFile ? getFileExt(selectedFile.name) : null

  return (
    <div className="space-y-4">
      {!selectedFile ? (
        <div
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={() => setDragOver(false)}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
            dragOver
              ? 'border-clinical-500 bg-clinical-50'
              : 'border-gray-300 hover:border-clinical-400 hover:bg-gray-50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".pdf,.docx,.doc,.txt,.md,.png,.jpg,.jpeg,.tiff,.bmp"
            onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])}
          />
          <Upload className={`h-12 w-12 mx-auto mb-4 ${dragOver ? 'text-clinical-500' : 'text-gray-400'}`} />
          <p className="text-lg font-medium text-gray-700">Drop a clinical document here</p>
          <p className="text-sm text-gray-500 mt-1">Supports PDF, DOCX, TXT, and image files</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {isImage(selectedFile.name) ? (
                <Image className="h-5 w-5 text-green-500" />
              ) : isPdf(selectedFile.name) ? (
                <File className="h-5 w-5 text-red-500" />
              ) : (
                <FileText className="h-5 w-5 text-gray-500" />
              )}
              <div>
                <p className="font-medium text-gray-900 text-sm">{selectedFile.name}</p>
                <p className="text-xs text-gray-500">{formatSize(selectedFile.size)} — {ext.toUpperCase()}</p>
              </div>
            </div>
            <button
              onClick={() => { setSelectedFile(null); setError(null) }}
              className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {hasPreview ? (
            <div className="p-2">
              {isPdf(selectedFile.name) && previewUrl && (
                <iframe
                  src={previewUrl}
                  className="w-full h-[500px] border-0 rounded"
                  title={selectedFile.name}
                />
              )}
              {isImage(selectedFile.name) && previewUrl && (
                <img
                  src={previewUrl}
                  alt={selectedFile.name}
                  className="max-w-full max-h-[500px] mx-auto rounded"
                />
              )}
              {textContent !== null && (
                <pre className="p-4 text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed overflow-auto max-h-[500px] bg-gray-50 rounded">
                  {textContent}
                </pre>
              )}
            </div>
          ) : (
            <div className="p-8 text-center">
              <FileText className="h-10 w-10 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">
                {ext === 'docx' ? 'DOCX preview not available. Click Generate to process.' : 'Preview not available for this file type.'}
              </p>
            </div>
          )}
        </div>
      )}

      {selectedFile && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-clinical-600 text-white font-medium rounded-lg hover:bg-clinical-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? (
            <>
              <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              Generate
            </>
          )}
        </button>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
          <div>
            <p className="font-medium text-red-800">Error</p>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      )}
    </div>
  )
}
