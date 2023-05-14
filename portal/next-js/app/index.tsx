'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface ZoomRoom {
  room_number: string;
  zoom_link: string;
}

interface Updates {
  id: number;
  message?: string;
  start_date: number;
  end_date: number;
}

interface Availability {
  id: number;
  department: string;
  course_name: string;
  number: number;
  tutors: string[];
}

interface OfficeHours {
  day_of_week: string;
  open_at: string;
  close_at: string;
}

export interface IndexProps {
  updates: Updates[];
  zoom: ZoomRoom;
  hours: OfficeHours[];
  availability: Availability[];
}

const IndexPage = ({ updates, zoom, hours, availability }: IndexProps) => {
  const router = useRouter();

  return (
    <>
      <h1>WELCOME TO THE UNO CSLC</h1>
      <h2>
        {' '}
        {zoom.room_number} | <Link href={zoom.zoom_link}>Zoom Link</Link>
      </h2>
      <br />
      <hr className="solid" />

      {updates.map((update) => (
        <h5 key={update.id}>{update.message}</h5>
      ))}

      <h1 style={{ fontSize: '20px' }}>HOURS</h1>

      <div className="container" style={{ textAlign: 'center' }}>
        <div className="row">
          {hours.map(({ day_of_week: dayOfWeek, open_at: openAt, close_at: closeAt }) => {
            return (
              <div className="col" key={dayOfWeek}>
                <h5>{dayOfWeek}</h5>
                {openAt} - {closeAt}
              </div>
            );
          })}
        </div>

        <br />
        <div className="row">
          <div className="col-12">
            <button
              className="create-ticket-button"
              onClick={() => router.push('/create-ticket')}
              data-toggle="tooltip"
              data-placement="top"
              title="hii"
            >
              Open Ticket
            </button>
          </div>
        </div>

        <hr className="solid" />
        <h1>COURSE AVAILABILITY</h1>
        <table>
          <thead>
            <tr>
              <th>
                <h2>Course</h2>
              </th>
              <th>
                <h2>Tutors</h2>
              </th>
            </tr>
          </thead>
          <tbody>
            {availability.map(({ id, department, number, course_name: courseName, tutors }) => {
              return (
                <tr key={id} className="middle" data-toggle="tooltip" data-placement="top" title={tutors.join(', ')}>
                  <td>{`${department} ${number}: ${courseName}`}</td>
                  <td>{tutors?.length}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
};

export default IndexPage;
