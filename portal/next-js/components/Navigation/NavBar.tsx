import UnauthenticatedView from './views/unauthenticated';
import TutorView from './views/tutor';
import AdminView from './views/admin';

export interface NavBarProps {
  id?: number;
  email?: string;
  name?: string;
  isAuthenticated: boolean;
  permission?: 'Owner' | 'Admin' | 'Tutor' | 'Student';
}

const NavBar = ({ isAuthenticated, permission }: NavBarProps) => {
  const permissionComponent = {
    Owner: (
      <>
        <TutorView />
        <AdminView />
      </>
    ),
    Tutor: <TutorView />,
    Admin: <AdminView />,
    Student: <>???</>,
  };

  if (!isAuthenticated) {
    return <UnauthenticatedView />;
  }

  return (
    <div className="nav-section">
      <ul>
        <li className="nav-link">
          <a className="Login" href={`${process.env.NEXT_PUBLIC_FLASK_APP_URL}/logout`}>
            Logout
          </a>
        </li>

        {permission && permissionComponent[permission]}
      </ul>
    </div>
  );
};

export default NavBar;
