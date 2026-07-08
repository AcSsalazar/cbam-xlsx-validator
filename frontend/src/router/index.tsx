import { createBrowserRouter } from "react-router-dom";

import { AppLayout } from "../layout/AppLayout";
import { Home } from "../pages/Home";
import { RecordsPage } from "../pages/RecordsPage";

export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { path: "/", element: <Home /> },
      { path: "/records", element: <RecordsPage /> },
    ],
  },
]);
