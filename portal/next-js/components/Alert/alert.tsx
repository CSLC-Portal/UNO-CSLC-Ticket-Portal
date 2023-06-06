import { AlertClasses } from 'types/enum';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useEffect, useState } from 'react';

interface AlertProps {
  state: AlertClasses;
  message: string;
  onClose?: Function;
}

const Alert = ({ state, message, onClose }: AlertProps) => {
  const [hideAlert, setHideAlert] = useState(false);

  useEffect(() => {
    if (hideAlert) onClose?.();
  }, [onClose, hideAlert]);

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
