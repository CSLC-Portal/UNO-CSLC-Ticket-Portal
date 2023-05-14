'use client';
import Alert from '@components/Alert/alert';
import { ReactElement, SyntheticEvent, useCallback, useState } from 'react';
import { AlertClasses } from 'types/enum';
interface CreateTicketProps {
  user: User;
  // NOTE: API does query.all() for each of these
  courses: Course[];
  sections: Section[];
  problemTypes: ProblemType[];
}

const CreateTicket = ({ user, courses, sections, problemTypes }: CreateTicketProps) => {
  const [alert, setAlert] = useState<ReactElement | null>(null);
  const onCloseAlert = () => setAlert(null);

  const onFormSubmit = async (event: SyntheticEvent) => {
    event.preventDefault();
    const errorAlert = (
      <Alert
        state={AlertClasses.ERROR}
        message="Something went wrong, please try again or contact support if the problem persists"
        onClose={onCloseAlert}
      />
    );

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/create-ticket`, { mode: 'no-cors' });

      if (res.status === 200) {
        setAlert(<Alert state={AlertClasses.PRIMARY} message="Successfully submitted ticket" onClose={onCloseAlert} />);
      } else {
        setAlert(errorAlert);
      }
    } catch (e) {
      setAlert(errorAlert);
    }
  };

  return (
    <div className="container p-3 gy-3">
      {alert}

      <div className="row">
        <div className="col">
          <h1>Create Ticket</h1>
          <hr />
        </div>
      </div>

      <div className="row">
        <form
          className=""
          action={`${process.env.NEXT_PUBLIC_API_URL}/create-ticket`}
          onSubmit={onFormSubmit}
          method="POST"
        >
          {!user.isAuthenticated && (
            <div className="mb-3">
              <h6>Contact Information</h6>
              <div className="form-floating mb-3">
                <input type="email" className="form-control" placeholder="name@example.com" required />
                <label>Email</label>
              </div>

              <div className="form-floating mb-3">
                <input type="text" className="form-control" placeholder="Full Name" required />
                <label>Full Name</label>
              </div>
            </div>
          )}

          <div className="row mb-3">
            <div className="col">
              <h6>Course Information</h6>
              <div className="input-group">
                <select className="form-select" style={{ lineHeight: '3.0' }} id="course_select" name="course" required>
                  <option value={''} disabled hidden>
                    Select Course
                  </option>
                  {courses.map(({ id, courseName }) => (
                    <option key={id} value={id}>
                      {courseName}
                    </option>
                  ))}
                </select>

                <select className="form-select" id="section_select" name="section" required hidden>
                  <option value={''} disabled hidden>
                    Select Section
                  </option>
                  {sections.map(({ id, courseId, sectionNumber }) => (
                    <option key={id} id={courseId.toString()} value={id}>
                      {sectionNumber}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="mb-3">
            <h6>Assignment Details</h6>

            <div className="form-floating mb-3">
              <input
                type="text"
                className="form-control"
                id="assignment"
                placeholder="Assignment Name"
                name="assignment"
                required
              />
              <label>Assignment Name</label>
            </div>

            <div className="mb-3">
              <textarea
                className="form-control"
                id="question"
                rows={10}
                placeholder="Description of issue or question..."
                name="question"
                required
              ></textarea>
              <label className="visually-hidden">Specific Question</label>
            </div>

            <div className="mb-3">
              <label>Problem Type</label>
              <select className="form-select" style={{ lineHeight: '3.0' }} id="problem" name="problem">
                {problemTypes.map(({ id, type }) => (
                  <option key={id} value={id}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mb-3">
            <h6>Please select in person or online mode of help</h6>
            <div className="form-check">
              <input
                type="radio"
                id="inPersonRadio"
                name="mode"
                className="form-check-input"
                value="{{ Mode.InPerson.value }}"
                required
              />
              <label className="form-check-label">In Person</label>
            </div>
            <div className="form-check">
              <input
                type="radio"
                id="onlineRadio"
                name="mode"
                className="form-check-input"
                value="{{ Mode.Online.value }}"
                required
              />
              <label className="form-check-label">Online</label>
            </div>
          </div>

          <hr />

          <div className="d-flex justify-content-center">
            <input type="submit" className="btn w-25 btn-lg btn-primary" value="Submit" />
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateTicket;
