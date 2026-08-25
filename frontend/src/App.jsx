import { BrowserRouter, Routes, Route } from 'react-router-dom'
import UploadPage from './pages/UploadPage'
import DocumentsPage from './pages/DocumentsPage'
import DetailPage from './pages/DetailPage'
import PatientsPage from './pages/PatientsPage'
import Navbar from './components/Navbar'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<DocumentsPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/documents/:id" element={<DetailPage />} />
            <Route path="/patients" element={<PatientsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
