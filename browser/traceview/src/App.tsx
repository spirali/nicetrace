import './App.css'
import { SummaryPage } from './components/SummaryPage'

import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import "./index.css";
import { TracePage } from './components/TracePage';


function App(props: { url: string }) {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <SummaryPage url={props.url} />,
    },
    {
      path: "traces/:traceId",
      element: <TracePage url={props.url} />,
    }
  ]);
  return <RouterProvider router={router} />
}

export default App
