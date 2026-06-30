import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import client from '../api/client'
import { HideDetail as HideDetailType } from '../types/hide'
import ImageViewer from '../components/ui/ImageViewer'

export default function HideDetail() {
  const { opId, hideId } = useParams<{ opId: string; hideId: string }>()
  const navigate = useNavigate()

  const [hide, setHide] = useState<HideDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setHide(null)
    setNotFound(false)
    setError(null)
    client
      .get<HideDetailType>(`/hides/${hideId}`)
      .then((res) => setHide(res.data))
      .catch((err) => {
        if (err.response?.status === 404) setNotFound(true)
        else setError('Erro ao carregar dados do couro')
      })
      .finally(() => setLoading(false))
  }, [hideId])

  const navigateToHide = (id: number) => navigate(`/ops/${opId}/hides/${id}`)

  if (loading) return <p>Carregando...</p>
  if (notFound)
    return (
      <p>
        Couro não encontrado. <Link to={`/ops/${opId}`}>Voltar para a OP</Link>
      </p>
    )
  if (error) return <p>{error}</p>
  if (!hide) return null

  return (
    <div>
      <h1>Couro {hide.hide_num}</h1>

      <section>
        <p>OP: <Link to={`/ops/${hide.op}`}>{hide.op}</Link></p>
        <p>Data/Hora: {new Date(hide.processed_at).toLocaleString('pt-BR')}</p>
        <p>Classe: {hide.class}</p>
        <p>Aproveitamento: {hide.yield_pct != null ? `${hide.yield_pct.toFixed(1)}%` : '—'}</p>
        <p>Área: {hide.area != null ? `${hide.area.toFixed(2)} m²` : '—'}</p>
      </section>

      <section>
        {hide.image_available ? (
          <ImageViewer
            src={`${client.defaults.baseURL}/hides/${hide.id}/image`}
            alt={`Couro ${hide.hide_num}`}
          />
        ) : (
          <p>Imagem não disponível</p>
        )}
      </section>

      <div>
        <button
          disabled={hide.prev_hide_id === null}
          onClick={() => hide.prev_hide_id !== null && navigateToHide(hide.prev_hide_id)}
        >
          Couro anterior
        </button>
        <button
          disabled={hide.next_hide_id === null}
          onClick={() => hide.next_hide_id !== null && navigateToHide(hide.next_hide_id)}
        >
          Próximo couro
        </button>
        <Link to={`/ops/${opId}`}>Voltar para a OP</Link>
      </div>
    </div>
  )
}
