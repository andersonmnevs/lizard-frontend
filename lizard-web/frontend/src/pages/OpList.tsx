import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import client from '../api/client'
import { OpListResponse } from '../types/op'
import OpTable from '../components/tables/OpTable'
import Pagination from '../components/ui/Pagination'

export default function OpList() {
  const [searchParams, setSearchParams] = useSearchParams()

  const page = Number(searchParams.get('page') || '1')
  const search = searchParams.get('search') || ''
  const dateFrom = searchParams.get('date_from') || ''
  const dateTo = searchParams.get('date_to') || ''
  const classFilter = searchParams.get('class') || ''

  const [localSearch, setLocalSearch] = useState(search)
  const [localDateFrom, setLocalDateFrom] = useState(dateFrom)
  const [localDateTo, setLocalDateTo] = useState(dateTo)
  const [localClass, setLocalClass] = useState(classFilter)

  const [data, setData] = useState<OpListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)

    const params: Record<string, string> = { page: String(page), limit: '20' }
    if (search) params.search = search
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    if (classFilter) params.class = classFilter

    client
      .get<OpListResponse>('/ops', { params })
      .then((res) => setData(res.data))
      .catch(() => setError('Erro ao carregar lista de OPs'))
      .finally(() => setLoading(false))
  }, [page, search, dateFrom, dateTo, classFilter])

  const handleFilter = () => {
    const next: Record<string, string> = { page: '1' }
    if (localSearch) next.search = localSearch
    if (localDateFrom) next.date_from = localDateFrom
    if (localDateTo) next.date_to = localDateTo
    if (localClass) next.class = localClass
    setSearchParams(next)
  }

  const handlePageChange = (newPage: number) => {
    const next: Record<string, string> = { page: String(newPage) }
    if (search) next.search = search
    if (dateFrom) next.date_from = dateFrom
    if (dateTo) next.date_to = dateTo
    if (classFilter) next.class = classFilter
    setSearchParams(next)
  }

  return (
    <div>
      <h1>Lista de OPs</h1>

      <div>
        <input
          type="date"
          value={localDateFrom}
          onChange={(e) => setLocalDateFrom(e.target.value)}
          placeholder="Data início"
        />
        <input
          type="date"
          value={localDateTo}
          onChange={(e) => setLocalDateTo(e.target.value)}
          placeholder="Data fim"
        />
        <select value={localClass} onChange={(e) => setLocalClass(e.target.value)}>
          <option value="">Todas as classes</option>
          <option value="A">A</option>
          <option value="B">B</option>
          <option value="C">C</option>
          <option value="D">D</option>
        </select>
        <input
          type="text"
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          placeholder="Buscar por OP"
        />
        <button onClick={handleFilter}>Filtrar</button>
      </div>

      {loading && <p>Carregando...</p>}
      {error && <p>{error}</p>}
      {!loading && !error && data && (
        <>
          <OpTable items={data.items} />
          {data.pages > 1 && (
            <Pagination
              page={data.page}
              pages={data.pages}
              onPageChange={handlePageChange}
            />
          )}
        </>
      )}
    </div>
  )
}
