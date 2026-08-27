import { FileText, AlertTriangle } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function SummaryPanel({ extraction }) {
  if (!extraction?.summary) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
        <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
        <p className="text-yellow-800">No summary available</p>
      </div>
    )
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <div className="px-4 py-3 bg-clinical-50 border-b border-clinical-100 flex items-center gap-2">
        <FileText className="h-4 w-4 text-clinical-600" />
        <h3 className="font-semibold text-clinical-800">Clinical Summary</h3>
      </div>
      <div className="p-5">
        <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed">
          <ReactMarkdown>{extraction.summary}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
