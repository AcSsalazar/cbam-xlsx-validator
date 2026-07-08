import { createBrowserRouter } from "react-router-dom";

import { Home } from "../pages/Home";
import { RecordsPage } from "../pages/RecordsPage";
import { UploadPage } from "../pages/UploadPage";

export const router = createBrowserRouter([
  { path: "/", element: <Home /> },
  { path: "/upload", element: <UploadPage /> },
  { path: "/records", element: <RecordsPage /> },
]);
