import { Link } from 'react-router-dom'
import Header from '../components/Header.jsx'
import Hero from '../components/Hero.jsx'
import ClickUpFormEmbed from '../components/ClickUpFormEmbed.jsx'
import Footer from '../components/Footer.jsx'

const FORM_URL = 'https://forms.clickup.com/9014421433/f/8cmu9xt-14274/487EVW1HFMQEO835RS'

export default function ChromebookRepair() {
  return (
    <>
      <Header />
      <main>
        <Hero
          title="Media Specialist Chromebook Repair"
          description="Submit a repair request below for a Chromebook that is damaged or not working."
        />
        <ClickUpFormEmbed src={FORM_URL} title="Media Specialist Chromebook Repair form" />
        <p style={{ marginTop: '1.5rem' }}>
          <Link to="/media-specialist-helpdesk">&larr; Back to Media Specialist Portal</Link>
        </p>
      </main>
      <Footer />
    </>
  )
}
