import { useNavigate } from 'react-router-dom'
import FileUpload from '../components/FileUpload'

export default function UploadPage() {
  const navigate = useNavigate()
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Document</h1>
        <p className="text-gray-500 mt-1">
          Upload a clinical document for AI-powered extraction and analysis
        </p>
      </div>
      <FileUpload onUploadComplete={(res) => {
        setTimeout(() => navigate(`/documents/${res.document_id}`), 1500)
      }} />
    </div>
  )
}
