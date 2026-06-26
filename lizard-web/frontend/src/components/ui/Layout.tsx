import { Link, Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <>
      <header>
        <span>Lizard Web</span>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/ops">Lista de OPs</Link>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </>
  )
}
