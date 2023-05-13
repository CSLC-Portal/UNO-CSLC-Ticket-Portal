import Link from 'next/link';

const AdminView = () => (
  <li className="nav-link">
    <div>
      <button
        className="btn btn-secondary shadow-none dropdown-toggle"
        type="button"
        id="dropdownMenuButton1"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        Admin
      </button>
      <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">
        <li>
          <Link className="dropdown-item" href="/view/admin/console">
            Administration Console
          </Link>
        </li>
        <li>
          <Link className="dropdown-item" href="/view/admin/reports-form">
            Reports
          </Link>
        </li>
      </ul>
    </div>
  </li>
);

export default AdminView;
