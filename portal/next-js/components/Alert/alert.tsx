import { AlertClasses } from 'types/enum';
import 'bootstrap/dist/css/bootstrap.min.css';

interface AlertProps {
  state: AlertClasses;
  message: string;
}

const Alert = ({ state, message }: AlertProps) => {
  return (
    <>
      <div className={`alert alert-${state} alert-dismissible fade show fixed-top`} role="alert">
        {message}
        <button type="button" className="btn-close" data-bs-dismiss="alert" aria-label="Close" />
      </div>
    </>
  );
};

export default Alert;
