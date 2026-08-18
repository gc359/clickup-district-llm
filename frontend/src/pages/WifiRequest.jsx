import Header from '../components/Header.jsx'
import ComingSoon from '../components/ComingSoon.jsx'
import Footer from '../components/Footer.jsx'

export default function WifiRequest() {
  return (
    <>
      <Header />
      <main>
        <ComingSoon
          title="WiFi Your Phone"
          description="Self-service BYOD onboarding is coming soon. In the meantime, contact the IT helpdesk or use the chat widget for help connecting a personal device to the district network."
        />
      </main>
      <Footer />
    </>
  )
}
