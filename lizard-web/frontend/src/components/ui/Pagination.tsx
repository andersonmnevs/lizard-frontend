interface Props {
  page: number
  pages: number
  onPageChange: (page: number) => void
}

export default function Pagination({ page, pages, onPageChange }: Props) {
  return (
    <div>
      <button disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
        Anterior
      </button>
      <span>
        Página {page} de {pages}
      </span>
      <button disabled={page >= pages} onClick={() => onPageChange(page + 1)}>
        Próximo
      </button>
    </div>
  )
}
