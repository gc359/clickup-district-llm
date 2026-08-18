import Header from '../components/Header.jsx'
import ComingSoon from '../components/ComingSoon.jsx'
import Footer from '../components/Footer.jsx'

export default function IdRequest() {
  return (
    <>
      <Header />
      <main>
        <ComingSoon
          title="ID Request"
          description="Ordering a new or replacement staff or student ID badge online is coming soon. Contact the IT helpdesk directly in the meantime."
        />
      </main>
      <Footer />
    </>
  )
}
