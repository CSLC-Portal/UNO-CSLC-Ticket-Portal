import CreateTicket from './create-ticket';

export default function Page() {
  // Mock data
  const user: User = { isAuthenticated: false };
  const courses: Course[] = [{ id: 1, courseName: 'CS101' }];
  const sections: Section[] = [{ id: 1, courseId: 1, sectionNumber: 101 }];
  const problemTypes: ProblemType[] = [
    { id: 0, type: 'What if...' },
    { id: 1, type: 'Another problem type :o' },
  ];

  const props = {
    user,
    courses,
    sections,
    problemTypes,
  };

  return <CreateTicket {...props} />;
}
