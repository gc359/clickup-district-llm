import Header from '../components/Header.jsx'
import Hero from '../components/Hero.jsx'
import ClickUpFormEmbed from '../components/ClickUpFormEmbed.jsx'
import Footer from '../components/Footer.jsx'

const FORM_URL = 'https://forms.clickup.com/9014421433/f/8cmu9xt-1394/VD6ZUUD0H5MCHPEH3R'
const PIERCE_GMAIL_URL =
  'https://mail.google.com/mail/?view=cm&fs=1&to=jpierce@bloomfield.k12.nj.us'

export default function TicketRequest() {
  return (
    <>
      <Header />
      <main>
        <Hero
          title="Request Tech Support"
          description="Submit a ticket below for hardware, software, or account issues. For quick answers, try the chat widget in the corner first."
        />
        <p className="notice-callout" role="note">
          <strong>PowerSchool questions?</strong> For all PowerSchool information and support,
          please contact Dr. Pierce{' '}
          <a href={PIERCE_GMAIL_URL} target="_blank" rel="noopener noreferrer">
            here
          </a>
          .
        </p>
        <ClickUpFormEmbed src={FORM_URL} title="Request Tech Support form" />
      </main>
      <Footer />
    </>
  )
}
