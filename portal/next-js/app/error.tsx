'use client';

import Alert from '@components/Alert/alert';
import { AlertClasses } from 'types/enum';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <h1 style={{ fontSize: '20px' }}>Oops..</h1>
      <br />
      Sorry, we are having some technical difficulties.
      <br />
      Try refreshing the page or contacting support if the problem persists
      <br />
      <Alert message="Something went wrong" state={AlertClasses.ERROR} />
    </div>
  );
}
