import Header from '../components/Header.jsx'
import ComingSoon from '../components/ComingSoon.jsx'
import Footer from '../components/Footer.jsx'

export default function TicketRequest() {
  return (
    <>
      <Header />
      <main>
        <ComingSoon
          title="Request Tech Support"
          description="A full-page ticket form is coming soon. For now, open the chat widget in the corner and choose &ldquo;Submit a ticket&rdquo; to file a support request."
        />
      </main>
      <Footer />
    </>
  )
}
