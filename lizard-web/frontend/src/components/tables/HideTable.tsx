import { Link } from 'react-router-dom'
import { HideItem } from '../../types/hide'

interface Props {
  items: HideItem[]
  opId: string
}

export default function HideTable({ items, opId }: Props) {
  if (items.length === 0) return <p>Nenhum couro encontrado.</p>

  return (
    <table>
      <thead>
        <tr>
          <th>Couro</th>
          <th>Data/Hora</th>
          <th>Classe</th>
          <th>Aproveitamento</th>
          <th>Área (m²)</th>
        </tr>
      </thead>
      <tbody>
        {items.map((hide) => (
          <tr key={hide.id}>
            <td>
              <Link to={`/ops/${opId}/hides/${hide.id}`}>{hide.hide_num}</Link>
            </td>
            <td>{new Date(hide.processed_at).toLocaleString('pt-BR')}</td>
            <td>{hide.class}</td>
            <td>{hide.yield_pct != null ? `${hide.yield_pct.toFixed(1)}%` : '—'}</td>
            <td>{hide.area != null ? hide.area.toFixed(2) : '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
