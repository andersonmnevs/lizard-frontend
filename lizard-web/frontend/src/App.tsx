import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/ui/Layout'
import Dashboard from './pages/Dashboard'
import OpList from './pages/OpList'
import OpDetail from './pages/OpDetail'
import HideDetail from './pages/HideDetail'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="ops" element={<OpList />} />
          <Route path="ops/:id" element={<OpDetail />} />
          <Route path="ops/:opId/hides/:hideId" element={<HideDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
