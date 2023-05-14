import IndexPage, { IndexProps } from './index';

export default async function Page() {
  // let props = {} as IndexProps;

  // const data = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/home`, { cache: 'no-store' });

  // if (data.status === 200) {
  //   const json = await data.json();
  //   props = json;
  // }

  const props: IndexProps = {
    availability: [{ id: 1, number: 1, tutors: ['Micheal'], course_name: 'Intro to CS', department: 'IT' }],
    hours: [{ day_of_week: 'Monday', open_at: '8:00am', close_at: '8:00pm' }],
    updates: [{ id: 1, message: 'An update for you', start_date: 123, end_date: 123 }],
    zoom: { room_number: 'abc 123', zoom_link: 'https://duck.com' },
  };

  return <IndexPage {...props} />;
}
