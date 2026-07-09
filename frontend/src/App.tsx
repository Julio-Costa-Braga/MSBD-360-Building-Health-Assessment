import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import NewInspection from './pages/NewInspection'
import InspectionDetail from './pages/InspectionDetail'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/inspections/new" element={<NewInspection />} />
        <Route path="/inspections/:id" element={<InspectionDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
