import Header from '../components/Header.jsx'
import Hero from '../components/Hero.jsx'
import ClickUpFormEmbed from '../components/ClickUpFormEmbed.jsx'
import Footer from '../components/Footer.jsx'

const FORM_URL = 'https://forms.clickup.com/9014421433/f/8cmu9xt-10274/1Y9ZK3KUWYES4VUMK9'

export default function WifiRequest() {
  return (
    <>
      <Header />
      <main>
        <Hero
          title="WiFi Your Phone"
          description="Complete the form below to connect your personal device to the district network."
        />
        <ClickUpFormEmbed src={FORM_URL} title="WiFi Your Phone form" />
      </main>
      <Footer />
    </>
  )
}
