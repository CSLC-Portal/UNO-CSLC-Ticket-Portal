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
          <a className="dropdown-item" href="{{ url_for('admin.console') }}">
            Administration Console
          </a>
        </li>
        <li>
          <a className="dropdown-item" href="{{ url_for('admin.reports_form') }}">
            Reports
          </a>
        </li>
      </ul>
    </div>
  </li>
);

export default AdminView;
