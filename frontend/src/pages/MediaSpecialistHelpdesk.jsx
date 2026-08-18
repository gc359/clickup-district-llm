import Header from '../components/Header.jsx'
import ComingSoon from '../components/ComingSoon.jsx'
import Footer from '../components/Footer.jsx'

export default function MediaSpecialistHelpdesk() {
  return (
    <>
      <Header />
      <main>
        <ComingSoon
          title="Media Specialist Portal"
          description="Chromebook repairs and device requests for librarians are coming soon. This staff-only portal is not yet available &mdash; contact the IT helpdesk directly in the meantime."
        />
      </main>
      <Footer />
    </>
  )
}
