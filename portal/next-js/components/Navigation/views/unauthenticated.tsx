import Link from 'next/link';

const UnauthenticatedView = () => (
  <div className="nav-section">
    <ul>
      <li>
        <Link className="Login" href="{{ build_auth_url() }}">
          Sign In
        </Link>
      </li>
    </ul>
  </div>
);

export default UnauthenticatedView;
