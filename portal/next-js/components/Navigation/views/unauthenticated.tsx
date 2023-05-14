import Link from 'next/link';

const UnauthenticatedView = () => (
  <div className="nav-section">
    <ul>
      <li>
        <Link className="Login" href={`${process.env.NEXT_PUBLIC_FLASK_APP_URL}/sign-in`}>
          Sign In
        </Link>
      </li>
    </ul>
  </div>
);

export default UnauthenticatedView;
