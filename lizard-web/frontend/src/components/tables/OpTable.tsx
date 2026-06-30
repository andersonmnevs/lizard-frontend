import { Link } from 'react-router-dom'
import { OpSummary } from '../../types/op'

interface Props {
  items: OpSummary[]
}

export default function OpTable({ items }: Props) {
  if (items.length === 0) return <p>Nenhuma OP encontrada.</p>

  return (
    <table>
      <thead>
        <tr>
          <th>OP</th>
          <th>Data</th>
          <th>Couros</th>
          <th>Aproveitamento</th>
          <th>Classe Predominante</th>
        </tr>
      </thead>
      <tbody>
        {items.map((op) => (
          <tr key={op.op}>
            <td>
              <Link to={`/ops/${op.op}`}>{op.op}</Link>
            </td>
            <td>
              {op.last_updated
                ? new Date(op.last_updated).toLocaleDateString('pt-BR')
                : '—'}
            </td>
            <td>{op.total_hides}</td>
            <td>{op.avg_yield != null ? `${op.avg_yield.toFixed(1)}%` : '—'}</td>
            <td>{op.predominant_class ?? '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
