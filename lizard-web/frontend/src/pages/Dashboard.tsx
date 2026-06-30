import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client'
import { DashboardData } from '../types/op'
import ClassDistributionChart from '../components/charts/ClassDistributionChart'

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    client
      .get<DashboardData>('/dashboard')
      .then((res) => setData(res.data))
      .catch(() => setError('Erro ao carregar dados do dashboard'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Carregando...</p>
  if (error) return <p>{error}</p>
  if (!data) return null

  return (
    <div>
      <h1>Dashboard</h1>

      <section>
        <h2>Hoje</h2>
        <p>Total de couros: {data.today.total_hides}</p>
        <p>
          Aproveitamento médio:{' '}
          {data.today.avg_yield !== null ? `${data.today.avg_yield}%` : '—'}
        </p>
      </section>

      <section>
        <h2>Semana</h2>
        <p>Total de couros: {data.week.total_hides}</p>
        <p>
          Aproveitamento médio:{' '}
          {data.week.avg_yield !== null ? `${data.week.avg_yield}%` : '—'}
        </p>
      </section>

      <section>
        <h2>Distribuição de Classes (Hoje)</h2>
        {data.today_class_distribution.length > 0 ? (
          <ClassDistributionChart data={data.today_class_distribution} />
        ) : (
          <p>Sem dados de classificação para hoje.</p>
        )}
      </section>

      <section>
        <h2>Últimas OPs</h2>
        {data.recent_ops.length > 0 ? (
          <ul>
            {data.recent_ops.map((op) => (
              <li key={op.op}>
                <Link to={`/ops/${op.op}`}>{op.op}</Link>
                {' — '}{op.date} — {op.total_hides} couros
              </li>
            ))}
          </ul>
        ) : (
          <p>Nenhuma OP recente.</p>
        )}
      </section>
    </div>
  )
}
