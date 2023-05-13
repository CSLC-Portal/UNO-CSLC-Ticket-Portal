const TutorView = () => (
  <li className="nav-link">
    <div>
      <button
        className="btn btn-secondary shadow-none dropdown-toggle"
        type="button"
        id="dropdownMenuButton1"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        Tutor
      </button>
      <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">
        <li>
          <a className="dropdown-item" href="{{ url_for('views.view_info') }}">
            Edit Tutor Information
          </a>
        </li>
        <li>
          <a className="dropdown-item" href="{{ url_for('views.view_tickets') }}">
            View Tickets
          </a>
        </li>
      </ul>
    </div>
  </li>
);

export default TutorView;
