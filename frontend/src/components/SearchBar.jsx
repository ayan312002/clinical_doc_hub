import { useState, useEffect } from 'react'
import { Search, X } from 'lucide-react'
import { searchDocuments } from '../api/client'
import DocumentCard from './DocumentCard'

export default function SearchBar({ onResults }) {
  const [query, setQuery] = useState('')
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    if (!query.trim()) {
      onResults?.(null)
      return
    }
    const timer = setTimeout(async () => {
      setSearching(true)
      try {
        const res = await searchDocuments(query)
        onResults?.(res.results)
      } catch {
        onResults?.([])
      } finally {
        setSearching(false)
      }
    }, 400)
    return () => clearTimeout(timer)
  }, [query])

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search documents, patients, diagnoses..."
        className="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-clinical-500 focus:border-clinical-500 outline-none"
      />
      {query && (
        <button
          onClick={() => setQuery('')}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >
          <X className="h-4 w-4" />
        </button>
      )}
      {searching && (
        <div className="absolute right-10 top-1/2 -translate-y-1/2">
          <div className="h-4 w-4 border-2 border-clinical-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
    </div>
  )
}
