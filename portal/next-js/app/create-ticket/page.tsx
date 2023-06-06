import CreateTicket from './create-ticket';

export default async function Page() {
  let response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/current_user`, { cache: 'no-store' });
  const user = await response.json();

  response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/get-all-courses`);
  const courses: Course[] = await response.json();

  response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/get-all-sections`);
  const sections: Section[] = await response.json();

  response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/get-all-problem-types`);
  const problemTypes: ProblemType[] = await response.json();

  const props = {
    user,
    courses,
    sections,
    problemTypes,
  };

  return <CreateTicket {...props} />;
}
