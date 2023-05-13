import Alert from '@components/Alert/alert';
import { AlertClasses } from 'types/enum';

const Index = () => {
  return <Alert state={AlertClasses.PRIMARY} message={'Alerts are working'} />;
};

export default Index;
