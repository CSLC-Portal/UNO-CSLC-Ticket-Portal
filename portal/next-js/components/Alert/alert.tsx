import { AlertClasses } from 'types/enum';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useState } from 'react';

interface AlertProps {
  state: AlertClasses;
  message: string;
}

const Alert = ({ state, message }: AlertProps) => {
  const [hideAlert, setHideAlert] = useState(false);

  return (
    <>
      {!hideAlert && (
        <div className={`alert alert-${state} alert-dismissible fade show fixed-top`} role="alert">
          {message}
          <button type="button" className="btn-close" aria-label="Close" onClick={() => setHideAlert(true)} />
        </div>
      )}
    </>
  );
};

export default Alert;
