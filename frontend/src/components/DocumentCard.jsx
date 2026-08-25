import { Link } from 'react-router-dom'
import { FileText, Clock, AlertTriangle, CheckCircle, Loader } from 'lucide-react'

const triageColors = {
  critical: 'bg-red-100 text-red-800 border-red-200',
  high: 'bg-orange-100 text-orange-800 border-orange-200',
  routine: 'bg-blue-100 text-blue-800 border-blue-200',
  normal: 'bg-green-100 text-green-800 border-green-200',
}

const statusIcons = {
  uploaded: <Clock className="h-4 w-4 text-gray-400" />,
  processing: <Loader className="h-4 w-4 text-yellow-500 animate-spin" />,
  completed: <CheckCircle className="h-4 w-4 text-green-500" />,
  failed: <AlertTriangle className="h-4 w-4 text-red-500" />,
}

const docTypeLabels = {
  discharge_summary: 'Discharge Summary',
  lab_report: 'Lab Report',
  intake_form: 'Intake Form',
  physician_notes: 'Physician Notes',
  imaging_report: 'Imaging Report',
  medication_list: 'Medication List',
  consultation: 'Consultation',
  unknown: 'Unknown',
}

export default function DocumentCard({ doc }) {
  return (
    <Link
      to={`/documents/${doc.id}`}
      className="block bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-clinical-300 transition-all"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <FileText className="h-5 w-5 text-clinical-500 mt-0.5" />
          <div>
            <p className="font-medium text-gray-900 truncate max-w-md">{doc.filename}</p>
            <p className="text-sm text-gray-500">
              {docTypeLabels[doc.doc_type] || doc.doc_type}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {doc.triage_level && (
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${triageColors[doc.triage_level] || ''}`}>
              {doc.triage_level}
            </span>
          )}
          <div className="flex items-center gap-1">
            {statusIcons[doc.status]}
            <span className="text-xs text-gray-500 capitalize">{doc.status}</span>
          </div>
        </div>
      </div>
      {doc.patient_mrn && (
        <p className="text-xs text-gray-400 mt-2">MRN: {doc.patient_mrn}</p>
      )}
      <p className="text-xs text-gray-400 mt-1">
        {doc.created_at ? new Date(doc.created_at).toLocaleString() : ''}
      </p>
    </Link>
  )
}
