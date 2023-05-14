import IndexPage, { IndexProps } from './index';

export default async function Page() {
  let props = {} as IndexProps;

  const data = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/home`, { cache: 'no-store' });

  if (data.status === 200) {
    const json = await data.json();
    props = json;
  }

  return <IndexPage {...props} />;
}
