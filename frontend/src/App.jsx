import { Route, Routes } from 'react-router-dom'
import ChatWidget from './components/chat/ChatWidget.jsx'
import Landing from './pages/Landing.jsx'
import Agent from './pages/Agent.jsx'
import WifiRequest from './pages/WifiRequest.jsx'
import TicketRequest from './pages/TicketRequest.jsx'
import TrainingRequest from './pages/TrainingRequest.jsx'
import IdRequest from './pages/IdRequest.jsx'
import MediaSpecialistHelpdesk from './pages/MediaSpecialistHelpdesk.jsx'

export default function App() {
  return (
    <>
      <ChatWidget />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/agent" element={<Agent />} />
        <Route path="/wifi-request" element={<WifiRequest />} />
        <Route path="/ticket-request" element={<TicketRequest />} />
        <Route path="/training-request" element={<TrainingRequest />} />
        <Route path="/id-request" element={<IdRequest />} />
        <Route path="/media-specialist-helpdesk" element={<MediaSpecialistHelpdesk />} />
        <Route path="*" element={<Landing />} />
      </Routes>
    </>
  )
}
