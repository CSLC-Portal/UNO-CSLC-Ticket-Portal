import UnauthenticatedView from './views/unauthenticated';
import TutorView from './views/tutor';
import AdminView from './views/admin';

interface NavBar {}

const NavBar = ({}: NavBar) => {
  // Would receive this data from..somewhere idk yet.
  const userIsAuthenticated = false;
  const userPermission = '';

  const permissionComponent = {
    tutor: <TutorView />,
    admin: <AdminView />,
  };

  if (!userIsAuthenticated) {
    return <UnauthenticatedView />;
  }

  return (
    <div className="nav-section">
      <ul>
        <li className="nav-link">
          <a className="Login" href="{{ url_for('auth.logout') }}">
            Logout
          </a>
        </li>

        {userPermission && permissionComponent[userPermission]}
      </ul>
    </div>
  );
};

export default NavBar;
