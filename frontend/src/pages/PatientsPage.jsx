import { useState, useEffect } from 'react'
import { listPatients } from '../api/client'
import { Users, AlertTriangle, FileText } from 'lucide-react'
import { Link } from 'react-router-dom'

const triageColors = {
  critical: 'bg-red-100 text-red-800',
  high: 'bg-orange-100 text-orange-800',
  routine: 'bg-blue-100 text-blue-800',
  normal: 'bg-green-100 text-green-800',
}

export default function PatientsPage() {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listPatients().then(setPatients).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="h-8 w-8 border-2 border-clinical-500 border-t-transparent rounded-full animate-spin mx-auto" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
        <p className="text-gray-500 mt-1">{patients.length} patient profile{patients.length !== 1 ? 's' : ''}</p>
      </div>

      {patients.length === 0 ? (
        <div className="text-center py-12 bg-white border border-gray-200 rounded-xl">
          <Users className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No patient profiles yet</p>
          <p className="text-sm text-gray-400 mt-1">Upload documents with patient MRNs to create profiles</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {patients.map((p) => (
            <div key={p.id} className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-all">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{p.name || 'Unknown'}</h3>
                  <p className="text-sm text-gray-500">MRN: {p.mrn}</p>
                </div>
                {p.latest_triage && (
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${triageColors[p.latest_triage]}`}>
                    {p.latest_triage}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <FileText className="h-3.5 w-3.5" />
                  {p.document_count} doc{p.document_count !== 1 ? 's' : ''}
                </span>
                {p.dob && <span>DOB: {p.dob}</span>}
              </div>
              <p className="text-xs text-gray-400 mt-3">
                Updated: {p.updated_at ? new Date(p.updated_at + 'Z').toLocaleDateString() : ''}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
