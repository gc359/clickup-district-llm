import Header from '../components/Header.jsx'
import Hero from '../components/Hero.jsx'
import ClickUpFormEmbed from '../components/ClickUpFormEmbed.jsx'
import Footer from '../components/Footer.jsx'

const FORM_URL = 'https://forms.clickup.com/9014421433/f/8cmu9xt-1394/VD6ZUUD0H5MCHPEH3R'

export default function TicketRequest() {
  return (
    <>
      <Header />
      <main>
        <Hero
          title="Request Tech Support"
          description="Submit a ticket below for hardware, software, or account issues. For quick answers, try the chat widget in the corner first."
        />
        <ClickUpFormEmbed src={FORM_URL} title="Request Tech Support form" />
      </main>
      <Footer />
    </>
  )
}
