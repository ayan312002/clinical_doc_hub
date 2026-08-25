import { useState, useRef } from 'react'
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import { uploadDocument } from '../api/client'

export default function FileUpload({ onUploadComplete }) {
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleFile = async (file) => {
    setUploading(true)
    setError(null)
    setResult(null)
    try {
      const res = await uploadDocument(file)
      setResult(res)
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

  return (
    <div className="space-y-4">
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
        <p className="text-lg font-medium text-gray-700">
          {uploading ? 'Uploading...' : 'Drop a clinical document here'}
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Supports PDF, DOCX, TXT, and image files
        </p>
      </div>

      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
          <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
          <div>
            <p className="font-medium text-green-800">Upload successful</p>
            <p className="text-sm text-green-600">
              {result.filename} — {result.message}
            </p>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
          <div>
            <p className="font-medium text-red-800">Upload failed</p>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      )}
    </div>
  )
}
