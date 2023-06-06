declare namespace NodeJS {
  export interface ProcessEnv {
    NEXT_PUBLIC_API_URL: string;
    NEXT_PUBLIC_FLASK_APP_URL: string;
  }
}

interface User {
  isAuthenticated: boolean;
}

interface Course {
  id: number;
  courseName: string;
}

interface Section {
  id: number;
  courseId: number;
  sectionNumber: number;
}

interface ProblemType {
  id: number;
  type: string;
}
