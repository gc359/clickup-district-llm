import Header from '../components/Header.jsx'
import ComingSoon from '../components/ComingSoon.jsx'
import Footer from '../components/Footer.jsx'

export default function TrainingRequest() {
  return (
    <>
      <Header />
      <main>
        <ComingSoon
          title="Tech-ED Training"
          description="Requesting technology training or professional development is coming soon. Contact the IT helpdesk directly in the meantime."
        />
      </main>
      <Footer />
    </>
  )
}
