import IndexPage, { IndexProps } from './index';

export default async function Page() {
  let props = { error: true } as IndexProps;

  try {
    const data = await fetch(process.env.NEXT_PUBLIC_API_URL, { cache: 'no-store' });
    if (data.status === 200) {
      const json = await data.json();
      console.log(json);

      props = { ...json, error: false };
    }
  } catch (err) {}

  return <IndexPage {...props} />;
}
