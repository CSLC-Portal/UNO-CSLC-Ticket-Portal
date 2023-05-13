import Alert from '@components/Alert/alert';
import { AlertClasses } from 'types/enum';

export default function Index() {
  return (
    <>
      <Alert state={AlertClasses.PRIMARY} message="Alerts are working" />
    </>
  );
}
