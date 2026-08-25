import { Pill, TestTube, AlertTriangle, Heart, Activity, User } from 'lucide-react'

function ConfidenceBadge({ score }) {
  if (score == null) return null
  const pct = Math.round(score * 100)
  const color = pct >= 80 ? 'text-green-600 bg-green-50' : pct >= 50 ? 'text-yellow-600 bg-yellow-50' : 'text-red-600 bg-red-50'
  return (
    <span className={`text-xs px-1.5 py-0.5 rounded ${color}`}>
      {pct}%
    </span>
  )
}

function Section({ title, icon: Icon, children, count }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center gap-2">
        <Icon className="h-4 w-4 text-clinical-600" />
        <h3 className="font-semibold text-gray-800">{title}</h3>
        {count != null && (
          <span className="text-xs bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded-full">{count}</span>
        )}
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}

function FieldRow({ label, value, confidence }) {
  if (!value && value !== 0) return null
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-gray-50 last:border-0">
      <span className="text-sm text-gray-600">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-gray-900">{String(value)}</span>
        <ConfidenceBadge score={confidence} />
      </div>
    </div>
  )
}

export default function ExtractionCard({ extraction }) {
  const diagnoses = extraction.diagnoses || []
  const medications = extraction.medications || []
  const labResults = extraction.lab_results || []
  const vitalSigns = extraction.vital_signs || []
  const procedures = extraction.procedures || []
  const allergies = extraction.allergies || []
  const riskFlags = extraction.risk_flags || []
  const confidence = extraction.confidence_scores || {}

  return (
    <div className="space-y-4">
      {/* Patient Info */}
      <Section title="Patient Information" icon={User}>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <FieldRow label="Name" value={extraction.patient_name} />
          <FieldRow label="DOB" value={extraction.patient_dob} />
          <FieldRow label="MRN" value={extraction.patient_mrn} />
          <FieldRow label="Admission" value={extraction.admission_date} />
          <FieldRow label="Discharge" value={extraction.discharge_date} />
          <FieldRow label="Physician" value={extraction.attending_physician} />
        </div>
      </Section>

      {/* Risk Flags */}
      {riskFlags.length > 0 && (
        <Section title="Risk Flags" icon={AlertTriangle} count={riskFlags.length}>
          <div className="space-y-2">
            {riskFlags.map((flag, i) => (
              <div key={i} className="flex items-start gap-2 p-2 bg-red-50 rounded-lg">
                <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-red-800">{flag}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Diagnoses */}
      <Section title="Diagnoses" icon={Activity} count={diagnoses.length}>
        {diagnoses.length === 0 ? (
          <p className="text-sm text-gray-400">None extracted</p>
        ) : (
          <div className="space-y-1">
            {diagnoses.map((d, i) => (
              <div key={i} className="flex items-center justify-between py-1.5 border-b border-gray-50 last:border-0">
                <span className="text-sm text-gray-600">{d.name}</span>
                <ConfidenceBadge score={d.confidence} />
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* Medications */}
      <Section title="Medications" icon={Pill} count={medications.length}>
        {medications.length === 0 ? (
          <p className="text-sm text-gray-400">None extracted</p>
        ) : (
          <div className="space-y-2">
            {medications.map((m, i) => (
              <div key={i} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">{m.name}</span>
                  <ConfidenceBadge score={m.confidence} />
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {[m.dosage, m.frequency, m.route].filter(Boolean).join(' — ')}
                </div>
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* Lab Results */}
      <Section title="Lab Results" icon={TestTube} count={labResults.length}>
        {labResults.length === 0 ? (
          <p className="text-sm text-gray-400">None extracted</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 font-medium">Test</th>
                  <th className="pb-2 font-medium">Value</th>
                  <th className="pb-2 font-medium">Range</th>
                  <th className="pb-2 font-medium">Flag</th>
                  <th className="pb-2 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {labResults.map((lab, i) => (
                  <tr key={i} className="border-b border-gray-50">
                    <td className="py-2 text-gray-900">{lab.test_name}</td>
                    <td className="py-2 font-medium">
                      {lab.value} {lab.unit}
                    </td>
                    <td className="py-2 text-gray-500">{lab.reference_range}</td>
                    <td className="py-2">
                      {lab.flag && (
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          lab.flag.includes('critical') ? 'bg-red-100 text-red-800' :
                          lab.flag.includes('abnormal') ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {lab.flag}
                        </span>
                      )}
                    </td>
                    <td className="py-2"><ConfidenceBadge score={lab.confidence} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Section>

      {/* Vital Signs */}
      <Section title="Vital Signs" icon={Heart} count={vitalSigns.length}>
        {vitalSigns.length === 0 ? (
          <p className="text-sm text-gray-400">None extracted</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {vitalSigns.map((v, i) => (
              <div key={i} className="p-2 bg-gray-50 rounded-lg text-center">
                <p className="text-xs text-gray-500">{v.name}</p>
                <p className="font-medium text-gray-900">{v.value} {v.unit}</p>
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* Procedures & Allergies */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Section title="Procedures" icon={Activity} count={procedures.length}>
          {procedures.length === 0 ? (
            <p className="text-sm text-gray-400">None extracted</p>
          ) : (
            <ul className="space-y-1">
              {procedures.map((p, i) => (
                <li key={i} className="text-sm text-gray-700">- {p}</li>
              ))}
            </ul>
          )}
        </Section>
        <Section title="Allergies" icon={AlertTriangle} count={allergies.length}>
          {allergies.length === 0 ? (
            <p className="text-sm text-gray-400">None extracted</p>
          ) : (
            <ul className="space-y-1">
              {allergies.map((a, i) => (
                <li key={i} className="text-sm text-red-700 font-medium">{a}</li>
              ))}
            </ul>
          )}
        </Section>
      </div>

      {/* Confidence Scores */}
      {Object.keys(confidence).length > 0 && (
        <Section title="Confidence Scores" icon={Activity}>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(confidence).map(([key, score]) => (
              <div key={key} className="text-center p-2 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500 capitalize">{key.replace(/_/g, ' ')}</p>
                <p className={`text-lg font-bold ${
                  score >= 0.8 ? 'text-green-600' : score >= 0.5 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {Math.round(score * 100)}%
                </p>
              </div>
            ))}
          </div>
        </Section>
      )}
    </div>
  )
}
