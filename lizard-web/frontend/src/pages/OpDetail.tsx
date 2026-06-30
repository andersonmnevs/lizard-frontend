import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import client from '../api/client'
import { OpDetail as OpDetailType } from '../types/op'
import { HideListResponse } from '../types/hide'
import ClassDistributionChart from '../components/charts/ClassDistributionChart'
import HideTable from '../components/tables/HideTable'
import Pagination from '../components/ui/Pagination'

export default function OpDetail() {
  const { id } = useParams<{ id: string }>()

  const [opData, setOpData] = useState<OpDetailType | null>(null)
  const [opLoading, setOpLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [opError, setOpError] = useState<string | null>(null)

  const [hidesData, setHidesData] = useState<HideListResponse | null>(null)
  const [hidesLoading, setHidesLoading] = useState(true)
  const [hidesError, setHidesError] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  useEffect(() => {
    setOpLoading(true)
    setNotFound(false)
    setOpError(null)
    client
      .get<OpDetailType>(`/ops/${id}`)
      .then((res) => setOpData(res.data))
      .catch((err) => {
        if (err.response?.status === 404) setNotFound(true)
        else setOpError('Erro ao carregar dados da OP')
      })
      .finally(() => setOpLoading(false))
  }, [id])

  useEffect(() => {
    setHidesLoading(true)
    setHidesError(null)
    client
      .get<HideListResponse>(`/ops/${id}/hides`, { params: { page, limit: 50 } })
      .then((res) => setHidesData(res.data))
      .catch(() => setHidesError('Erro ao carregar couros'))
      .finally(() => setHidesLoading(false))
  }, [id, page])

  if (opLoading) return <p>Carregando...</p>
  if (notFound)
    return (
      <p>
        OP não encontrada. <Link to="/ops">Voltar à lista</Link>
      </p>
    )
  if (opError) return <p>{opError}</p>
  if (!opData) return null

  return (
    <div>
      <h1>OP {opData.op}</h1>

      <section>
        <p>Total de couros: {opData.total_hides}</p>
        <p>Área média: {opData.avg_area != null ? `${opData.avg_area.toFixed(2)} m²` : '—'}</p>
        <p>
          Aproveitamento médio:{' '}
          {opData.avg_yield != null ? `${opData.avg_yield.toFixed(1)}%` : '—'}
        </p>
      </section>

      <section>
        <h2>Distribuição de Classes</h2>
        {opData.class_distribution.length > 0 ? (
          <ClassDistributionChart data={opData.class_distribution} />
        ) : (
          <p>Sem dados de classificação.</p>
        )}
      </section>

      <section>
        <h2>Couros</h2>
        {hidesLoading && <p>Carregando couros...</p>}
        {hidesError && <p>{hidesError}</p>}
        {!hidesLoading && !hidesError && hidesData && (
          <>
            <HideTable items={hidesData.items} opId={opData.op} />
            {hidesData.total > 50 && (
              <Pagination
                page={page}
                pages={Math.ceil(hidesData.total / 50)}
                onPageChange={setPage}
              />
            )}
          </>
        )}
      </section>
    </div>
  )
}
