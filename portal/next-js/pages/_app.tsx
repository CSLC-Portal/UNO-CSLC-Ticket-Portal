import type { AppProps } from 'next/app';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'styles/main-style.css';
import StickyHeader from '@components/Header/sticky-header';
import { useEffect } from 'react';
import NavBar from '@components/Navigation/NavBar';

export default function App({ Component, pageProps }: AppProps) {
  // Globally import bootstrap library for now
  useEffect(() => {
    require('bootstrap/dist/js/bootstrap.bundle.min');
  }, []);

  return (
    <div className="d-flex flex-column min-vh-100">
      <StickyHeader />
      <NavBar />

      <div id="content" className="container-fluid">
        <Component {...pageProps} />
      </div>

      <footer className="mt-auto" />
    </div>
  );
}
